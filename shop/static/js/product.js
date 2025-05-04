$(document).ready(function() {
    let product_id = $('input[name="product-id"]').val();

    setTimeout(function() {
        $.ajax({
            url: '/shop/view_handler/',
            type: 'PATCH',
            headers: {
                'X-CSRFToken': csrf_token
            },
            data: {
                'id': product_id
            },
            success: function(response) {
                console.log('Increased View Count')
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    }, 15000);

    $('.btn-add-wishlist').click(function(e) {
        e.preventDefault();

        let btn = $(this);

        btn.addClass('load-more-overlay loading');

        $.ajax({
            url: '/shop/like_handler/',
            type: 'PATCH',
            headers: {
                'X-CSRFToken': csrf_token
            },
            data: {
                'id': product_id
            },
            success: function(response) {
                btn.removeClass('load-more-overlay loading');
                if(response.like) {
                    $('.like-icon').css('color', 'red')
                } else {
                    $('.like-icon').css('color', '');
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
                btn.removeClass('load-more-overlay loading');
                if(xhr.status === 401) {
                    $('.login-toggle').click();
                }
            }
        });
    });
});
