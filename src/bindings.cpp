#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <hyprlang.hpp>
#include <any>
#include <stdexcept>
#include <string>
#include <vector>
#include <filesystem>

namespace py = pybind11;

static py::object anyToPython(const std::any& val) {
    if (!val.has_value())
        return py::none();

    const auto& t = val.type();
    if (t == typeid(int64_t))
        return py::int_(std::any_cast<int64_t>(val));
    if (t == typeid(float))
        return py::float_(std::any_cast<float>(val));
    if (t == typeid(const char*))
        return py::str(std::any_cast<const char*>(val));
    if (t == typeid(Hyprlang::SVector2D)) {
        auto v = std::any_cast<Hyprlang::SVector2D>(val);
        return py::make_tuple(v.x, v.y);
    }
    if (t == typeid(void*)) {
        auto p = std::any_cast<void*>(val);
        if (p)
            return py::int_(reinterpret_cast<intptr_t>(p));
        return py::none();
    }
    return py::none();
}

struct ConfigValueProxy {
    py::object value;
    bool       setByUser;
};

PYBIND11_MODULE(_core, m) {
    m.doc() = "Low-level Python bindings for hyprlang";

    py::class_<Hyprlang::SVector2D>(m, "SVector2D")
        .def(py::init<>())
        .def(py::init([](float x, float y) {
            return Hyprlang::SVector2D{x, y};
        }), py::arg("x"), py::arg("y"))
        .def_readwrite("x", &Hyprlang::SVector2D::x)
        .def_readwrite("y", &Hyprlang::SVector2D::y)
        .def("__repr__", [](const Hyprlang::SVector2D& v) {
            return "SVector2D(" + std::to_string(v.x) + ", " + std::to_string(v.y) + ")";
        })
        .def("__eq__", &Hyprlang::SVector2D::operator==);

    py::class_<Hyprlang::CParseResult>(m, "ParseResult")
        .def(py::init<>())
        .def_readwrite("error", &Hyprlang::CParseResult::error)
        .def_property_readonly("error_message", [](const Hyprlang::CParseResult& r) -> py::object {
            if (!r.error)
                return py::none();
            const char* msg = r.getError();
            if (msg)
                return py::str(msg);
            return py::none();
        })
        .def("__repr__", [](const Hyprlang::CParseResult& r) {
            if (!r.error)
                return std::string("ParseResult(ok)");
            const char* msg = r.getError();
            return std::string("ParseResult(error='") + (msg ? msg : "") + "')";
        })
        .def("__bool__", [](const Hyprlang::CParseResult& r) {
            return !r.error;
        });

    py::class_<Hyprlang::SConfigOptions>(m, "ConfigOptions")
        .def(py::init<>())
        .def_readwrite("verify_only", &Hyprlang::SConfigOptions::verifyOnly)
        .def_readwrite("throw_all_errors", &Hyprlang::SConfigOptions::throwAllErrors)
        .def_readwrite("allow_missing_config", &Hyprlang::SConfigOptions::allowMissingConfig)
        .def_readwrite("path_is_stream", &Hyprlang::SConfigOptions::pathIsStream);

    py::class_<Hyprlang::SHandlerOptions>(m, "HandlerOptions")
        .def(py::init<>())
        .def_readwrite("allow_flags", &Hyprlang::SHandlerOptions::allowFlags);

    py::class_<Hyprlang::SSpecialCategoryOptions>(m, "SpecialCategoryOptions")
        .def(py::init<>())
        .def_readwrite("ignore_missing", &Hyprlang::SSpecialCategoryOptions::ignoreMissing)
        .def_readwrite("anonymous_key_based", &Hyprlang::SSpecialCategoryOptions::anonymousKeyBased)
        .def("set_key", [](Hyprlang::SSpecialCategoryOptions& self, const std::string& key) {
            auto* copy = new std::string(key);
            self.key = copy->c_str();
        }, py::arg("key"));

    py::class_<ConfigValueProxy>(m, "ConfigValueProxy")
        .def_readonly("value", &ConfigValueProxy::value)
        .def_readonly("set_by_user", &ConfigValueProxy::setByUser)
        .def("__repr__", [](const ConfigValueProxy& p) {
            return "ConfigValueProxy(set_by_user=" + std::string(p.setByUser ? "True" : "False") + ")";
        });

    py::class_<Hyprlang::CConfig>(m, "Config")
        .def(py::init([](const std::string& path, const Hyprlang::SConfigOptions& opts) {
            try {
                return new Hyprlang::CConfig(path.c_str(), opts);
            } catch (const std::exception& e) {
                throw std::runtime_error(std::string("Failed to create config: ") + e.what());
            } catch (...) {
                throw std::runtime_error("Failed to create config for path: " + path);
            }
        }), py::arg("path"), py::arg("options") = Hyprlang::SConfigOptions{})

        .def("add_value", [](Hyprlang::CConfig& self, const std::string& name, py::object defaultVal) {
            if (py::isinstance<py::int_>(defaultVal)) {
                self.addConfigValue(name.c_str(), Hyprlang::CConfigValue((Hyprlang::INT)defaultVal.cast<int64_t>()));
            } else if (py::isinstance<py::float_>(defaultVal)) {
                self.addConfigValue(name.c_str(), Hyprlang::CConfigValue((Hyprlang::FLOAT)defaultVal.cast<float>()));
            } else if (py::isinstance<py::str>(defaultVal)) {
                self.addConfigValue(name.c_str(), Hyprlang::CConfigValue((Hyprlang::STRING)defaultVal.cast<std::string>().c_str()));
            } else if (py::isinstance<Hyprlang::SVector2D>(defaultVal)) {
                self.addConfigValue(name.c_str(), Hyprlang::CConfigValue(defaultVal.cast<Hyprlang::SVector2D>()));
            } else if (py::isinstance<py::tuple>(defaultVal) && py::len(defaultVal) == 2) {
                auto t = defaultVal.cast<py::tuple>();
                Hyprlang::SVector2D vec{t[0].cast<float>(), t[1].cast<float>()};
                self.addConfigValue(name.c_str(), Hyprlang::CConfigValue(vec));
            } else {
                throw std::invalid_argument("Unsupported default value type. Use int, float, str, SVector2D, or tuple(float, float).");
            }
        }, py::arg("name"), py::arg("default_value"))

        .def("commence", &Hyprlang::CConfig::commence)

        .def("parse", &Hyprlang::CConfig::parse)

        .def("parse_file", [](Hyprlang::CConfig& self, const std::string& path) {
            return self.parseFile(path.c_str());
        }, py::arg("path"))

        .def("parse_dynamic", [](Hyprlang::CConfig& self, const std::string& line) {
            return self.parseDynamic(line.c_str());
        }, py::arg("line"))

        .def("parse_dynamic_kv", [](Hyprlang::CConfig& self, const std::string& command, const std::string& value) {
            return self.parseDynamic(command.c_str(), value.c_str());
        }, py::arg("command"), py::arg("value"))

        .def("get_value", [](Hyprlang::CConfig& self, const std::string& name) -> py::object {
            auto val = self.getConfigValue(name.c_str());
            return anyToPython(val);
        }, py::arg("name"))

        .def("get_value_info", [](Hyprlang::CConfig& self, const std::string& name) -> ConfigValueProxy {
            auto* ptr = self.getConfigValuePtr(name.c_str());
            if (!ptr)
                throw std::runtime_error("Config value not found: " + name);
            return ConfigValueProxy{anyToPython(ptr->getValue()), ptr->m_bSetByUser};
        }, py::arg("name"))

        .def("add_special_category", [](Hyprlang::CConfig& self, const std::string& name, Hyprlang::SSpecialCategoryOptions opts) {
            self.addSpecialCategory(name.c_str(), opts);
        }, py::arg("name"), py::arg("options") = Hyprlang::SSpecialCategoryOptions{})

        .def("remove_special_category", [](Hyprlang::CConfig& self, const std::string& name) {
            self.removeSpecialCategory(name.c_str());
        }, py::arg("name"))

        .def("add_special_value", [](Hyprlang::CConfig& self, const std::string& cat, const std::string& name, py::object defaultVal) {
            if (py::isinstance<py::int_>(defaultVal)) {
                self.addSpecialConfigValue(cat.c_str(), name.c_str(), Hyprlang::CConfigValue((Hyprlang::INT)defaultVal.cast<int64_t>()));
            } else if (py::isinstance<py::float_>(defaultVal)) {
                self.addSpecialConfigValue(cat.c_str(), name.c_str(), Hyprlang::CConfigValue((Hyprlang::FLOAT)defaultVal.cast<float>()));
            } else if (py::isinstance<py::str>(defaultVal)) {
                self.addSpecialConfigValue(cat.c_str(), name.c_str(), Hyprlang::CConfigValue((Hyprlang::STRING)defaultVal.cast<std::string>().c_str()));
            } else if (py::isinstance<Hyprlang::SVector2D>(defaultVal)) {
                self.addSpecialConfigValue(cat.c_str(), name.c_str(), Hyprlang::CConfigValue(defaultVal.cast<Hyprlang::SVector2D>()));
            } else if (py::isinstance<py::tuple>(defaultVal) && py::len(defaultVal) == 2) {
                auto t = defaultVal.cast<py::tuple>();
                Hyprlang::SVector2D vec{t[0].cast<float>(), t[1].cast<float>()};
                self.addSpecialConfigValue(cat.c_str(), name.c_str(), Hyprlang::CConfigValue(vec));
            } else {
                throw std::invalid_argument("Unsupported default value type.");
            }
        }, py::arg("category"), py::arg("name"), py::arg("default_value"))

        .def("remove_special_value", [](Hyprlang::CConfig& self, const std::string& cat, const std::string& name) {
            self.removeSpecialConfigValue(cat.c_str(), name.c_str());
        }, py::arg("category"), py::arg("name"))

        .def("get_special_value", [](Hyprlang::CConfig& self, const std::string& cat, const std::string& name, py::object key) -> py::object {
            const char* keyPtr = key.is_none() ? nullptr : key.cast<std::string>().c_str();
            auto val = self.getSpecialConfigValue(cat.c_str(), name.c_str(), keyPtr);
            return anyToPython(val);
        }, py::arg("category"), py::arg("name"), py::arg("key") = py::none())

        .def("special_category_exists", [](Hyprlang::CConfig& self, const std::string& cat, const std::string& key) {
            return self.specialCategoryExistsForKey(cat.c_str(), key.c_str());
        }, py::arg("category"), py::arg("key"))

        .def("list_keys_for_special_category", [](Hyprlang::CConfig& self, const std::string& cat) {
            return self.listKeysForSpecialCategory(cat.c_str());
        }, py::arg("category"))

        .def("register_handler", [](Hyprlang::CConfig& self, const std::string& name, py::function callback, Hyprlang::SHandlerOptions opts) {
            auto cb = std::make_shared<py::function>(callback);

            auto trampoline = [cb](const char* command, const char* value) -> Hyprlang::CParseResult {
                Hyprlang::CParseResult result;
                py::gil_scoped_acquire gil;
                try {
                    py::object ret = (*cb)(py::str(command), py::str(value));
                    if (!ret.is_none() && py::isinstance<py::str>(ret)) {
                        std::string err = ret.cast<std::string>();
                        if (!err.empty()) {
                            result.error = true;
                            result.setError(err.c_str());
                        }
                    }
                } catch (py::error_already_set& e) {
                    result.error = true;
                    result.setError(e.what());
                }
                return result;
            };

            throw std::runtime_error(
                "register_handler with Python callables is not yet supported. "
                "Use the high-level API's on_keyword() or parse with handlers dict instead."
            );
        }, py::arg("name"), py::arg("callback"), py::arg("options") = Hyprlang::SHandlerOptions{})

        .def("unregister_handler", [](Hyprlang::CConfig& self, const std::string& name) {
            self.unregisterHandler(name.c_str());
        }, py::arg("name"))

        .def("change_root_path", [](Hyprlang::CConfig& self, const std::string& path) {
            self.changeRootPath(path.c_str());
        }, py::arg("path"));
}
