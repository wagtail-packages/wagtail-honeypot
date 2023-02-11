var whf_name = "whf_name";
var data_whf_name = "[data-" + whf_name + "]";

document.querySelectorAll(data_whf_name).forEach(function (el) {
    el.classList.add(whf_name);
    el.setAttribute("style", "position: absolute;top: 0;left: 0;margin-left: 100%;");
});