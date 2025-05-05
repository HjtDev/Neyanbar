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
                themeparsi.Minipopup.init();
                themeparsi.Minipopup.open({
                    message: `محصول با موفقیت ${response.like ? 'به علاقه مندی ها اضافه شد':'از علاقه مندی ها حذف شد'}!`,
                    productClass: 'product-wishlist',
                    name: $('h1.product-name').text(),
                    nameLink: window.location.href,
                    imageSrc: $('.product-thumb picture source').attr('srcset'),
                    imageLink: window.location.href,
                    // price: "۲۵۰,۰۰۰ تومان",
                    // count: 1,
                    // actionTemplate: '<div class="action-group d-flex"><a href="/account/dashboard/#likes" class="btn btn-sm btn-outline btn-primary btn-rounded">علاقه‌مندی‌ها</a></div>'
                });
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

    $('.btn-compare-product').click(function(e) {
        e.preventDefault();

        let btn = $(this);

        btn.addClass('load-more-overlay loading');

        $.ajax({
            url: '/account/dashboard/compare/action/',
            type: 'PATCH',
            headers: {
                'X-CSRFToken': csrf_token
            },
            data: {
                'id': product_id,
                'action': 'update'
            },
            success: function(response) {
                if(response.added) {
                    btn.html('<i class="fa-light fa-scale-balanced"></i> حذف از مقایسه ها');
                } else {
                    btn.html('<i class="fa-light fa-scale-balanced"></i> مقایسه');
                }
                btn.removeClass('load-more-overlay loading');
                themeparsi.Minipopup.init();
                themeparsi.Minipopup.open({
                    message: `محصول با موفقیت ${response.added ? 'به لیست مقایسه اضافه شد':'از لیست مقایسه حذف شد'}!`,
                    productClass: 'product-wishlist',
                    name: $('h1.product-name').text(),
                    nameLink: window.location.href,
                    imageSrc: $('.product-thumb picture source').attr('srcset'),
                    imageLink: window.location.href,
                    // price: "۲۵۰,۰۰۰ تومان",
                    count: 1,
                    actionTemplate: '<div class="action-group d-flex"><a href="/account/dashboard/compare/" class="btn btn-sm btn-outline btn-primary btn-rounded">لیست مقایسه</a></div>'
                });
            },
            error: function(xhr, status, error) {
                console.log(error);
                btn.removeClass('load-more-overlay loading');
                if(xhr.status === 401) {
                    $('.login-toggle').click();
                } else if(xhr.status === 403) {
                    themeparsi.Minipopup.init();
                    themeparsi.Minipopup.open({
                        message: `لیست مقایسه شما پر است!`,
                        productClass: 'product-wishlist',
                        name: $('h1.product-name').text(),
                        nameLink: window.location.href,
                        imageSrc: $('.product-thumb picture source').attr('srcset'),
                        imageLink: window.location.href,
                        // price: "۲۵۰,۰۰۰ تومان",
                        count: 1,
                        actionTemplate: '<div class="action-group d-flex"><a href="/account/dashboard/compare/" class="btn btn-sm btn-outline btn-primary btn-rounded">لیست مقایسه</a></div>'
                    });
                }
            }
        });
    });
});
