import os
import re
import json
from abc import ABC, abstractmethod
from datetime import datetime
import phonenumbers
import joblib
from email_validator import validate_email, EmailNotValidError
from auxiliary.util.global_constants import (
    WTS_PATH,
    CFG_PATH,
    ENC_PATH,
    SCL_ENC_PATH,
    LBL_ENC_PATH,
    KW_VEC_PATH,
)


_FILE_PATH = os.path.realpath(os.path.dirname(__file__))


class Plugin(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def apply(self):
        pass

    @abstractmethod
    def get_status(self):
        pass

    @abstractmethod
    def get_error(self):
        pass


class Split(Plugin):
    def __init__(self, kwargs):
        self._status = True
        self._error = None
        self._char = kwargs["char"]
        self._day = kwargs["day"]

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        split_data = str(x).split(self._char)
        return int(split_data[self._day])


class Isweekday(Plugin):
    def __init__(self, kwargs):
        self._status = True
        self._error = None

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        dt = datetime.strptime(str(x), "%Y-%m-%d %H:%M:%S")
        return int(dt.weekday() < 5)


class Timediff(Plugin):
    def __init__(self, kwargs):
        self._status = True
        self._error = None

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        x = datetime.strptime(x, "%Y-%m-%d")
        current_time = datetime.today()

        return current_time.year - x.year


class Weekofmonth(Plugin):
    def __init__(self, kwargs):
        self._status = True
        self._error = None

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        x = datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        x = x.date().day
        x = x / 7 + 1
        x = int(x)
        return x


class Timeofday(Plugin):
    def __init__(self, kwargs):
        self._status = True
        self._error = None

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        x = datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        self._hour = x.hour
        if 6 <= self._hour < 12:
            self._res = "Morning"
        elif 12 <= self._hour < 18:
            self._res = "Afternoon"
        else:
            self._res = "Evening/Night"

        return self._res


class Quarter(Plugin):
    def __init__(self, kwargs):
        self._status = True
        self._error = None

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        x = datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        return 1 + x.month / 4


class Createdmonth(Plugin):
    def __init__(self, kwargs):
        self._status = True
        self._error = None

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        x = datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        return x.month


class Substitute(Plugin):
    def __init__(self, kwargs):
        self._to = kwargs["to"]
        self._from = kwargs["from"]
        if isinstance(self._from, str):

            _FILE_PATH = os.path.realpath(os.path.dirname(__file__))
            config_path = os.path.join(_FILE_PATH, "configs")
            subst_path = os.path.join(config_path, self._from)

            if os.path.isfile(subst_path):
                self._data = json.load(open(subst_path))
            else:
                raise Exception("Config file not found")

            assert isinstance(self._from, str), (
                "'from' must be a list of strings: %s " % self._from
            )

        else:
            assert isinstance(self._from, list), (
                "'from' must be a list of strings: %s " % self._from
            )

        assert len(self._from) > 0, "Empty 'from' list : %s " % self._from
        assert self._to is not None, "Missing 'to' : %s " % self._to
        assert all([isinstance(k, str) for k in self._from]), (
            "'from' must be a list of strings: %s " % self._from
        )
        self._status = True
        self._error = None

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        if isinstance(self._from, str):
            for self._key, self._value in self._data.items():
                if x in self._value["from"]:
                    self._to = self._value["to"]
                    break
            return self._to
        else:
            return self._to if str(x) in self._from else x


class Regex(Plugin):
    def __init__(self, kwargs):
        try:
            self._to = kwargs["to"]
            self._from = kwargs["from"]
            self._reg_list = list(map(re.compile, self._from))
            assert type(self._from) == list, (
                "'from' must be a list of strings: %s " % self._from
            )
            assert len(self._from) > 0, "Empty 'from' list : %s " % self._from
            assert self._to is not None, "Missing 'to' : %s " % self._to
            assert all([type(k) == str for k in self._from]), (
                "'from' must be a list of strings: %s " % self._from
            )
            self._status = True
            self._error = None
        except Exception as ex:
            self._status = False
            self._error = ex

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        return self._to if any(regex.match(str(x)) for regex in self._reg_list) else x


class Fill_Na(Plugin):
    def __init__(self, kwargs):
        try:
            self._value = kwargs["value"]
            self._status = True
            self._error = None
        except Exception as ex:
            self._status = False
            self._error = ex

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):

        # TODO: Rewrite this logic better later
        val = True

        if x == "" or x is None:
            val = None

        return self._value if val is None else x


class Check_Presence(Plugin):
    def __init__(self, kwargs):
        try:
            self._status = True
            self._error = None
        except Exception as ex:
            self._status = False
            self._error = ex

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        val = True
        if x == "" or x is None:
            val = None
            return 0
        else:
            return 1


class Split_String(Plugin):
    def __init__(self, kwargs):
        self._status = True
        self._split = kwargs["split"]
        self._error = None

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        x = str(x)
        words = x.split(_split)

        if len(words) > 1:
            first_f = " ".join(words[:1]).strip()
            second_f = first_f.split("-")
            if len(second_f) > 2:
                return second_f[1]
            elif len(second_f) > 1:
                return second_f[-1]
            else:
                return first_f
        else:
            return x


class Check_Valid_Phone(Plugin):
    def __init__(self, kwargs):
        self._status = True
        self._error = None

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        try:
            phone_number = phonenumbers.parse("+1" + x)
            return phonenumbers.is_valid_number(phone_number)
        except:
            return False


class Get_Keyword_Vector(Plugin):

    encoders_path = os.path.join(_FILE_PATH, ENC_PATH)
    parent_path_to_vectoriser = os.path.join(encoders_path, KW_VEC_PATH)

    def __init__(self, kwargs):
        self._vector = kwargs["vector"]
        self._status = True
        self._error = None

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        vec_obj = joblib.load(
            f"{os.path(join(parent_path_to_vectoriser))}/{self._vector}"
        )
        tr_kw = vec_obj.transform([x]).toarray().tolist()
        wts = np.arange(15, 0, -1)
        np.average(tr_kw, weights=wts)


class Chech_Email_Validity(Plugin):
    def __init__(self, kwargs):
        self._status = True
        self._error = None

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        try:
            v = validate_email(email)
            email = v["email"]
            return True
        except EmailNotValidError as e:
            return False


class Extract_String(Plugin):
    def __init__(self, kwargs):
        try:
            self._regex = kwargs["regex"]
            self._status = True
            self._error = None
        except Exception as ex:
            self._status = False
            self._error = ex

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def apply(self, x):
        return x.str.extract(self._regex)


class Groups_Regex(Plugin):
    def __init__(self, kwargs):
        try:
            self._type = kwargs["type"]
            self._status = True
            self._error = None
        except Exception as ex:
            self._status = False
            self._error = ex

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def cleanup_url(url):

        url = (
            url.replace("https://", " ")
            .replace("www.", " ")
            .replace(".com/", " ")
            .strip()
        )

        re.sub(r"[^a-zA-Z0-9\s]+", " ", url)
        url = url.strip()
        wordlist = url.split()

        return wordlist

    def is_word_in_list(word, word_list, mapping_type):
        if mapping_type == "match":
            pattern = r"\b" + re.escape(word) + r"\b"
        elif mapping_type == "freeflow":
            pattern = re.escape(word)
        matches = [re.search(pattern, w) for w in word_list]
        return any(matches)

    def get_url_group(url):

        patterns = {
            "Medigap Plans by State": {
                "match": ["state", "states"],
                "freeflow": [],
                "exclude": [],
            },
            "Medigap Plans by Carrier": {
                "match": ["carrier", "medigap"],
                "freeflow": ["medigap"],
                "exclude": [],
            },
            "Medicare Coverage": {
                "match": ["coverage"],
                "freeflow": ["coverage"],
                "exclude": [],
            },
            "Other Plans": {"match": ["medigap plans"], "freeflow": [], "exclude": []},
            "Medicare Part C (Medicare Advantage)": {
                "match": ["advantage", "ma", "c"],
                "freeflow": ["part c", "advantage"],
                "exclude": [],
            },
            "Medicare Part D": {"match": ["d"], "freeflow": ["part d"], "exclude": []},
            "Medicare Supplements": {
                "match": ["ms"],
                "freeflow": ["supplement"],
                "exclude": [],
            },
            "FAQs": {"match": ["faq"], "freeflow": ["faq"], "exclude": []},
            "Compare": {"match": ["compare"], "freeflow": ["compare"], "exclude": []},
            "Other Topics": {"match": [], "freeflow": [], "exclude": []},
        }

        for class_name, pattern in patterns.items():

            wordlist = cleanup_url(url)

            mapped_1 = any(
                [is_word_in_list(word, wordlist, "match") for word in pattern["match"]]
            )
            mapped_2 = any(
                [
                    is_word_in_list(word, wordlist, "freeflow")
                    for word in pattern["freeflow"]
                ]
            )

            if mapped_1 or mapped_2:
                return class_name
        else:
            return "Others"

    def get_keyword_group(keyword):

        patterns = {
            "Health Insurance Medicare Supplement": {
                "match": ["health insurance medicare supplement"],
                "freeflow": [],
                "exclude": [],
            },
            "Medicare Supplement": {
                "match": ["medicare supplement plans", "supp"],
                "freeflow": ["supplement"],
                "exclude": [],
            },
            "Medicare Part D": {
                "match": ["d"],
                "freeflow": ["part d", "partd"],
                "exclude": [],
            },
            "Medigap Plans": {"match": ["gap"], "freeflow": ["medigap"], "exclude": []},
            "Medicare Plan F": {
                "match": ["f"],
                "freeflow": ["plan f", "planf"],
                "exclude": [],
            },
            "Medicare Plan N": {"match": ["n"], "freeflow": ["plan n"], "exclude": []},
            "Medicare Plan G": {
                "match": ["g"],
                "freeflow": ["plan g"],
                "exclude": ["plan n", "plan f", "part d"],
            },
            "Medicare Part C (Medicare Advantage)": {
                "match": ["medicare advantage", "advantage", "part c", "c"],
                "freeflow": ["part c"],
                "exclude": [],
            },
            "Medicare Coverage": {"match": [], "freeflow": ["coverage"], "exclude": []},
        }

        for class_name, pattern in patterns.items():

            wordlist = keyword.split()

            mapped_1 = any(
                [is_word_in_list(word, wordlist, "match") for word in pattern["match"]]
            )
            mapped_2 = any(
                [
                    is_word_in_list(word, wordlist, "freeflow")
                    for word in pattern["freeflow"]
                ]
            )

            if mapped_1 or mapped_2:
                return class_name
        else:
            return "Others"

    def apply(self, x):
        if self._type == "URL":
            return self.get_url_group(x)
        if self._type == "KW":
            return self.get_keyword_group(x)
