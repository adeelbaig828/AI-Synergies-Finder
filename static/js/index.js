console.log("Document is Loaded!")
var My_Profile_Data = null
var Other_Profile_Data = null
$(document).ready(function () {
    $("#GPT_Response_Div").hide()
    console.log("Document is Ready!")
})
function Render_PDF_Document() {
    Toogle_Loader_Modal(true)
    $(".My_Profile_Linked_URL_Input_Elements").each(function () {
        $(this).prop("disabled", true)
    });
    const fileInput = document.getElementById("PDF_Input_Element");
    const file = fileInput.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const pdfDisplay = document.getElementById("PDF_Displayer_div");
            const pdfContent = document.createElement("embed");
            pdfContent.setAttribute("src", e.target.result);
            pdfContent.setAttribute("type", "application/pdf");
            pdfContent.style.width = "100%";
            pdfContent.style.height = "500px";

            pdfDisplay.innerHTML = "";
            pdfDisplay.appendChild(pdfContent);
        };
        reader.readAsDataURL(file);
        Toogle_Loader_Modal(false)
        Read_PDF_Content(file)
    }

}


function Read_PDF_Content(PDF_File) {
    Toogle_Loader_Modal(true)
    const formData = new FormData();
    formData.append("pdf_file", PDF_File);
    FALCON_AI.AjaxCallWithFormData(
        "POST", "/api/extract_text/", formData, "JSON", (response) => {
            Toogle_Loader_Modal(false)
            My_Profile_Data = response.text
            console.log(My_Profile_Data)
        },
        (error) => {
            Toogle_Loader_Modal(false)
            console.log(error)
        }
        ,
        true,
        $('input[name=csrfmiddlewaretoken]').val(),
        FALCON_AI.Get_Access_Token()
    )
}

function Scrap_Data_By_URL(URL_Type) {
    Toogle_Loader_Modal(true)
    var formData = {}
    if (URL_Type == "My_Profile") {
        $(".My_Profile_PDF_File_Elements").each(function () {
            $(this).prop("disabled", true)
        });
        Input_Element_Id = "#My_Profile_Linked_URL_Input_Element"
        formData = { url: $(Input_Element_Id).val() }
        console.log(formData);
    }
    else {
        const falcon_ai_other_person_linked_url_form = $('#falcon_ai_other_person_linked_url_form');
        $.each(falcon_ai_other_person_linked_url_form.serializeArray(), function (_, field) {
            formData[field.name] = field.value;
        });
        Toggle_LinkedIn_URL_Modal(false)
    }


    FALCON_AI.AjaxCall(
        "POST", "/api/scrapping/", formData, "JSON", (response) => {
            Toogle_Loader_Modal(false)
            if (URL_Type == "My_Profile"){
                My_Profile_Data = response
                Toogle_Success_Modal(true,"Please Now Enter other Person profile URl")
            }
            else {

                Other_Profile_Data = response
                Fetch_One_Liner_And_Message_From_GPT()
            }
        },
        (error) => {
            Toogle_Loader_Modal(false)
            console.log(error)
        }
        ,
        true,
        $('input[name=csrfmiddlewaretoken]').val(),
        FALCON_AI.Get_Access_Token(),
        true
    )
}

function Toggle_LinkedIn_URL_Modal(Flag = true) {
    if (Flag) $("#Add_LinkedIn_URL_Modal").modal('show')
    else $("#Add_LinkedIn_URL_Modal").modal('hide')
}

function Fetch_One_Liner_And_Message_From_GPT() {
    formData={}
    const falcon_ai_other_person_linked_url_form = $('#falcon_ai_other_person_linked_url_form');
    $.each(falcon_ai_other_person_linked_url_form.serializeArray(), function (_, field) {
        formData[field.name] = field.value;
    });
    formData["my_profile_data"]=My_Profile_Data
    formData["other_profile_data"]=Other_Profile_Data
    formData["session_id"]=123
    FALCON_AI.AjaxCall(
        "POST", "/api/gpt_api/", formData, "JSON", (response) => {
            Toogle_Loader_Modal(false)
            console.log(response)
            $("#GPT_Response_Div").show()
            var textWithNewLines = response['success_response'];
            var formattedText = textWithNewLines.replace(/\n/g, "<br>");
            $("#GPT_Response_Element").html(formattedText);
        },
        (error) => {
            Toogle_Loader_Modal(false)
            console.log(error)
        }
        ,
        true,
        $('input[name=csrfmiddlewaretoken]').val(),
        FALCON_AI.Get_Access_Token(),
        true
    )
    // $.ajax({
    //     url: '/api/gpt_api/', // Replace with your API endpoint
    //     type: 'POST',
    //     data: JSON.stringify(payload),
    //     contentType: 'application/json',
    //     success: function (response) {
    //         Toogle_Loader_Modal(false)
    //         console.log(response)
    //         $("#GPT_Response_Div").show()
    //         var textWithNewLines = response['success_response'];
    //         var formattedText = textWithNewLines.replace(/\n/g, "<br>");
    //         $("#GPT_Response_Element").html(formattedText);
    //     },
    //     error: function (error) {
    //         Toogle_Loader_Modal(false)
    //         console.log(error);
    //     }
    // });
}

