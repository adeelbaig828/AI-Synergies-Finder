$(document).ready(function () {
    const form = $('#falcon_ai_login_form');
    form.find(':input').on('change', function() {
        FALCON_AI.Hide_Error_Div()
        console.log("Form field value changed!");
      });
    const signInButton = $('#falcon_ai_login_button');
    signInButton.on('click', function () {
        // Get form data
        const formData = {};
        $.each(form.serializeArray(), function (_, field) {
            formData[field.name] = field.value;
        });
        FALCON_AI.AjaxCall(
            "POST", "api/accounts/login/", formData, "JSON", (response) => {
                console.log(response)
                FALCON_AI.Set_Access_Token(response["access_token"])
                FALCON_AI.Set_Refresh_Token(response["refresh_token"])
                FALCON_AI.Set_Cookie("access_token",response["access_token"],1)
                window.location = "/home/"
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