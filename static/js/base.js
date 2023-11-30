BaseUrl = "192.168.18.49:8000/";
ShowUnAuthorizedErrorModal = function () {
    $("#UnAuthorizedErrorModal").show()
}
Toogle_Loader_Modal = function (Flag) {
    if (Flag) $("#Loader_Modal").modal('show')
    else $("#Loader_Modal").modal('hide')
}
Toogle_Success_Modal = function (Flag, Message) {
    if (Flag) {
        $("#Success_Modal").modal('show')
        $("#Success_Modal_Message").text(Message);
    }
    else $("#Loader_Modal").modal('hide')
}
RedirectToLogin = function () {
    FALCON_AI.Clear_Cookie("access_token")
    window.location = "/"
}

FALCON_AI = {

    AjaxCall: function (RequestType, RequestUrl, RequestData, RequestDataType, SuccessCallBackFunction, ErrorCallBackFunction, asyncBool, csrf_token, jwt_bearer_token, send_jwt_token = true) {
        if (RequestType == null)
            RequestType = "GET";
        if (RequestUrl == null)
            return "";
        if (RequestData == null)
            RequestData = "html";
        if (asyncBool == undefined || asyncBool == null)
            asyncBool = true;
        request_headers = {
            'X-CSRFToken': csrf_token, // Send the CSRF token in the request headers
            'Authorization': 'Bearer ' + jwt_bearer_token, // Replace <your_jwt_token> with the actual JWT token value
        }
        if (!send_jwt_token) request_headers = { 'X-CSRFToken': csrf_token, }
        $.ajax({
            type: RequestType,
            async: asyncBool,
            url: RequestUrl,
            headers: request_headers,
            data: RequestData,
            dataType: RequestDataType,
            success: function (result) {
                SuccessCallBackFunction(result, null, null);
            },
            error: function (ErrorObject, opts, error) {
                console.log(ErrorObject)

                if (typeof ErrorCallBackFunction == null || typeof ErrorCallBackFunction == 'undefined' || ErrorCallBackFunction == null) {
                    console.log(ErrorObject.responseText)
                }
                else {
                    ErrorCallBackFunction(ErrorObject.status, ErrorObject.responseJSON, "error");
                }
            }
        });
    },
    AjaxCallWithFormData: function (RequestType, RequestUrl, RequestData, RequestDataType, SuccessCallBackFunction, ErrorCallBackFunction, asyncBool, csrf_token, jwt_bearer_token) {
        if (RequestType == null)
            RequestType = "GET";
        if (RequestUrl == null)
            return "";
        if (RequestData == null)
            RequestData = "html";
        if (asyncBool == undefined || asyncBool == null)
            asyncBool = true;
        request_headers = {
            'X-CSRFToken': csrf_token, // Send the CSRF token in the request headers
            'Authorization': 'Bearer ' + jwt_bearer_token, // Replace <your_jwt_token> with the actual JWT token value
        }
        $.ajax({
            type: RequestType,
            async: asyncBool,
            url: RequestUrl,
            headers: request_headers,
            contentType: false,
            data: RequestData,
            processData: false,
            success: function (result) {
                SuccessCallBackFunction(result, null, null);
            },
            error: function (ErrorObject, opts, error) {
                if (ErrorObject.status == 401) {
                    ShowUnAuthorizedErrorModal()
                }
                if (typeof ErrorCallBackFunction == null || typeof ErrorCallBackFunction == 'undefined' || ErrorCallBackFunction == null) {
                    console.log(ErrorObject)
                }
                else {
                    ErrorCallBackFunction(ErrorObject.status, ErrorObject.responseText, "error");
                }
            }
        });
    },
    Set_Access_Token: function (access_token) {
        localStorage.setItem("access_token", access_token)
    },
    Get_Access_Token: function () {
        return localStorage.getItem("access_token")
    },
    Set_Refresh_Token: function (refresh_token) {
        localStorage.setItem("refresh_token", refresh_token)
    },
    Get_Refresh_Token: function () {
        return localStorage.getItem("refresh_token")
    },
    Show_Error_Div: function (error_message) {
        $("#error_div").removeClass("d-none")
        $("#error_p").text(error_message)
    },
    Hide_Error_Div: function () {
        $("#error_div").addClass("d-none")
        $("#error_p").text('')
    },
    Set_Cookie: function (cookieName, cookieValue, expirationDays) {
        var date = new Date();
        date.setTime(date.getTime() + (expirationDays * 24 * 60 * 60 * 1000));
        var cookieString = cookieName + "=" + encodeURIComponent(cookieValue);
        if (expirationDays) {
            cookieString += "; expires=" + date.toUTCString();
        }
        document.cookie = cookieString;
    },
    Clear_Cookie: function (cookieName) {
        document.cookie = cookieName + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
    }
}