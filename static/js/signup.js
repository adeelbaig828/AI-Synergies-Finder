$(document).ready(function () {
    const form = $('#falcon_ai_signup_form');
    const signInButton = $('#falcon_ai_signup_button');
    signInButton.on('click', function () {
        // Get form data
        const formData = {};
        $.each(form.serializeArray(), function (_, field) {
            formData[field.name] = field.value;
        });
        FALCON_AI.AjaxCall(
            "POST", "/api/accounts/signup/", formData, "JSON", (response) => {
                console.log(response)
                FALCON_AI.Set_Access_Token(response["access_token"])
                FALCON_AI.Set_Refresh_Token(response["refresh_token"])
                window.location = "/home/"
            },
            (error) => {
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