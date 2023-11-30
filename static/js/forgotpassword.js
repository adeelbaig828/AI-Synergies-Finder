$(document).ready(function () {
    const falcon_ai_otp_request_form = $('#falcon_ai_otp_request_form');
    const falcon_ai_otp_request_button = $('#falcon_ai_otp_request_button');
    const falcon_ai_forgot_password_form = $("#falcon_ai_forgot_password_form");
    const falcon_ai_forgot_password_button = $("#falcon_ai_forgot_password_button");
    falcon_ai_otp_request_form.find(':input').on('change', function() {
        FALCON_AI.Hide_Error_Div()
        console.log("Form field value changed!");
      });
      falcon_ai_forgot_password_form.find(':input').on('change', function() {
        FALCON_AI.Hide_Error_Div()
        console.log("Form field value changed!");
      });
    let email_or_username = ""
    falcon_ai_otp_request_button.on('click', function () {
        // Get form data
        const formData = {};
        $.each(falcon_ai_otp_request_form.serializeArray(), function (_, field) {
            formData[field.name] = field.value;
        });
        email_or_username = formData["email_or_username"]
        FALCON_AI.AjaxCall(
            "POST", "/api/accounts/forgot-password-request/", formData, "JSON", (response) => {
                console.log(response)
                falcon_ai_otp_request_form.addClass("d-none")
                falcon_ai_forgot_password_form.removeClass("d-none")
            },
            (code, error) => {
                FALCON_AI.Show_Error_Div(error['error'])
                console.log(error)
            }
            ,
            true,
            $('input[name=csrfmiddlewaretoken]').val(),
            null,
            false
        )
    });

    falcon_ai_forgot_password_button.on('click', function () {
        // Get form data
        const formData = {};
        $.each(falcon_ai_forgot_password_form.serializeArray(), function (_, field) {
            formData[field.name] = field.value;
        });
        formData["email_or_username"] = email_or_username
        FALCON_AI.AjaxCall(
            "POST", "/api/accounts/set-new-password/", formData, "JSON", (response) => {
                console.log(response)
                window.location = "/"
            },
            (code, error) => {
                FALCON_AI.Show_Error_Div(error['error'])
                console.log(error)
        
            }
            ,
            true,
            $('input[name=csrfmiddlewaretoken]').val(),
            null,
            false
        )
    });
});