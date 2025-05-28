let csrf_token = $('input[name="csrfmiddlewaretoken"]').val();

function setButtonLoading($btn, isLoading, btnText) {
    if (isLoading) {
        if (!$btn.data('original-html')) {
            $btn.data('original-html', $btn.html());
        }
        $btn.html(btnText + ' <span class="button-spinner"></span>');
        $btn.prop('disabled', true);
    } else {
        $btn.html((btnText ? btnText:$btn.data('original-html')));
        $btn.prop('disabled', false);
    }
}


$(document).ready(function () {
    $('.btn-login').click(function (e) {
        e.preventDefault();
        let btn = $(this);
        setButtonLoading(btn, true, '');

        let phone = $('#signin-phone').val();

        $.ajax({
            url: '/account/login/', type: 'POST', data: {
                'phone': phone, 'csrfmiddlewaretoken': csrf_token
            }, success: function (response) {
                console.log(response);
                setButtonLoading(btn, false, 'ورود');

                if (response.token_sent) {
                    btn.addClass('d-none');
                    $('#signin-phone').addClass('d-none');

                    $('.btn-submit-token').removeClass('d-none');
                    $('.btn-return').removeClass('d-none');
                    $('#token').removeClass('d-none');

                    $('#login-response').removeClass('d-none').text('کد تایید برای شما پیامک شد.');
                    $('.spam-alert').removeClass('d-none');
                }
            }, error: function (xhr, status, error) {
                console.log(error);
                setButtonLoading(btn, false, 'ورود');

                let errorMsg = 'خطایی رخ داده است.';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMsg = xhr.responseJSON.message;
                }

                $('#login-response').removeClass('d-none').text(errorMsg);
                $('.spam-alert').addClass('d-none');
            }
        });
    });

    $('.btn-submit-token').click(function (e) {
        e.preventDefault();
        let btn = $(this);
        setButtonLoading(btn, true, '');

        let phone = $('#signin-phone').val();
        let token = $('#token').val();
        console.log('Token:', token);

        $.ajax({
            url: '/account/login/complete/',
            type: 'POST',
            data: {
                'token': token,
                'phone': phone,
                'csrfmiddlewaretoken': csrf_token
            },
            success: function(response) {
                if(response.logged_in) {
                    console.log('Login Successfull');
                    setButtonLoading(btn, true, 'خوش آمدید');
                    setTimeout(function() {
                        // window.location.href = '/account/dashboard/';
                        window.location.href = window.location.origin + window.location.pathname; // same as a reload but removes the queries
                    }, 2000);
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
                setButtonLoading(btn, false, 'تایید');

                if(xhr.status === 406) {
                    btn.addClass('d-none');
                    $('#token').addClass('d-none').val('');

                    $('#signin-phone').removeClass('d-none');
                    $('.btn-login').removeClass('d-none');
                }

                let errorMsg = 'خطایی رخ داده است.';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMsg = xhr.responseJSON.message;
                }

                $('#login-response').removeClass('d-none').text(errorMsg);
            }
        });
    });

    $('.btn-register').click(function(e) {
        e.preventDefault();
        let btn = $(this);
        setButtonLoading(btn, true, '');
        let name = $('#register-name');
        let email = $('#register-email');
        let phone = $('#register-phone');

        $.ajax({
            url: '/account/register/',
            type: 'POST',
            data: {
                'name': name.val(),
                'email': email.val(),
                'phone': phone.val(),
                'csrfmiddlewaretoken': csrf_token
            },
            success: function(response) {
                if(response.token_sent) {

                    setButtonLoading(btn, false, 'ثبت نام')

                    name.addClass('d-none');
                    email.addClass('d-none');
                    phone.addClass('d-none');
                    btn.addClass('d-none')

                    $('#register-token').removeClass('d-none');
                    $('.btn-return').removeClass('d-none');
                    $('.btn-submit-register-token').removeClass('d-none');

                    $('#register-response').removeClass('d-none').text('کد تایید برای شما ارسال شد.');
                    $('.spam-alert').removeClass('d-none');
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
                setButtonLoading(btn, false, 'ثبت نام');

                let errorMsg = 'خطایی رخ داده است.';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMsg = xhr.responseJSON.message;
                }

                $('#register-response').removeClass('d-none').text(errorMsg);
            }
        });
    });

    $('.btn-submit-register-token').click(function(e) {
        e.preventDefault();
        let btn = $(this);
        setButtonLoading(btn, true, '');
        let name = $('#register-name');
        let email = $('#register-email');
        let phone = $('#register-phone');
        let token = $('#register-token');

        $.ajax({
            url: '/account/register/complete/',
            type: 'POST',
            data: {
                'name': name.val(),
                'email': email.val(),
                'phone': phone.val(),
                'token': token.val(),
                'csrfmiddlewaretoken': csrf_token
            },
            success: function(response) {
                if(response.logged_in) {
                    console.log('Register Successfull');
                    setButtonLoading(btn, true, 'خوش آمدید');
                    setTimeout(function() {
                        // window.location.href = '/account/dashboard/';
                        window.location.href = window.location.origin + window.location.pathname; // same as the reload but removes the queries
                    }, 1000);
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
                setButtonLoading(btn, false, 'تایید');

                if(xhr.status === 406) {
                    btn.addClass('d-none');
                    token.addClass('d-none').val('');

                    name.removeClass('d-none');
                    email.removeClass('d-none');
                    phone.removeClass('d-none');
                    $('.btn-register').removeClass('d-none');
                }

                let errorMsg = 'خطایی رخ داده است.';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMsg = xhr.responseJSON.message;
                }

                $('#register-response').removeClass('d-none').text(errorMsg);
            }
        });
    });

    $('.btn-return').click(function(e) {
        e.preventDefault();

        const baseUrl = window.location.origin + window.location.pathname;

        if ($('#register-token').hasClass('d-none')) {  // Login
            window.location.href = baseUrl + '?login=true';
        } else {  // Register
            window.location.href = baseUrl + '?register=true';
        }
    });
    setTimeout(function() {
        if(window.location.search) {
            const params = new URLSearchParams(window.location.search);
            if(params.get('login') === 'true') {
                console.log('trying to login')
                $('.login-toggle').click();
            } else if(params.get('register') === 'true') {
                $('.login-toggle').click();
                $('.register-sidebar-button').click();
            }
        }
    }, 1000);
});
