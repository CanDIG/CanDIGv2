// import { useSelector } from 'react-redux';

function getCookie(request, cookie_name) {
    if (!("Cookie" in request.Headers)) {
        return undefined;
    }
    var splitCookie = request.Headers["Cookie"][0].split("; ");
    var valueCookie = _.find(splitCookie, function (cookie) {
        if (cookie.indexOf(cookie_name + "=") > -1) {
            return cookie
        }
    });

    return valueCookie
}

module.exports = getCookie;
