$(document).ready(function() {
    let product_id = $('input[name="product-id"]').val();
    let selected_rating = 3

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
                if (response.like) {
                    $('.like-icon').css('color', 'red')
                } else {
                    $('.like-icon').css('color', '');
                }
                themeparsi.Minipopup.init();
                themeparsi.Minipopup.open({
                    message: `محصول با موفقیت ${response.like ? 'به علاقه مندی ها اضافه شد' : 'از علاقه مندی ها حذف شد'}!`,
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
                if (xhr.status === 401) {
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
                if (response.added) {
                    btn.html('<i class="fa-light fa-scale-balanced"></i> حذف از مقایسه ها');
                } else {
                    btn.html('<i class="fa-light fa-scale-balanced"></i> مقایسه');
                }
                btn.removeClass('load-more-overlay loading');
                themeparsi.Minipopup.init();
                themeparsi.Minipopup.open({
                    message: `محصول با موفقیت ${response.added ? 'به لیست مقایسه اضافه شد' : 'از لیست مقایسه حذف شد'}!`,
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
                if (xhr.status === 401) {
                    $('.login-toggle').click();
                } else if (xhr.status === 403) {
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
    $('.rate').click(function(e) {
        e.preventDefault();

        let btn = $(this);
        let rating = btn.data('rate');
        let rating_percent = rating * 20 + '%';
        btn.css('color', '#05595B').css('border-color', '#05595B');
        $('#rate-' + selected_rating).css('color', '#222').css('border-color', '');
        $('.rating-percent span').css('width', rating_percent)
        $('.progress-value').text(rating_percent);
        selected_rating = rating;
    });

    $('.submit-review-toggle').click(function(e) {
        e.preventDefault();

        let btn = $(this);
        let content = $('#review-message');

        if (!content) {
            return;
        }

        setButtonLoading(btn, true, 'در حال ارسال');


        $.ajax({
            url: '/shop/comment_handler/',
            type: 'POST',
            data: {
                'id': product_id,
                'score': selected_rating,
                'content': content.val(),
                'csrfmiddlewaretoken': csrf_token
            },
            success: function(response) {
                $('.comments-list').append(
                    `
                    <li>
                                                            <div class="comment">
                                                                <figure class="comment-media">
                                                                    <a href="#">
                                                                        <picture>
                                                                            <source srcset="${response.profile}"
                                                                                    type="image/webp">
                                                                            <img loading="lazy" decoding="async"
                                                                                 src="${response.profile}" alt="avatar">
                                                                        </picture>
                                                                    </a>
                                                                </figure>
                                                                <div class="comment-body">
                                                                    <div class="comment-rating ratings-container">
                                                                        <div class="ratings-full">
                                                                            <span class="ratings" style="width:${selected_rating * 20}%"></span>
                                                                            <span class="tooltiptext tooltip-top"></span>
                                                                        </div>
                                                                    </div>
                                                                    <div class="comment-user">
                                                                    <span class="comment-date">
                                                                        نویسنده :   <span
                                                                            class="font-weight-semi-bold text-dark">
                                                                            ${response.name}
                                                                        </span> در
                                                                        <span class="font-weight-semi-bold text-dark">
                                                                            ${response.created_at}
                                                                        </span>
                                                                    </span>
                                                                    </div>
                                                                    <div class="comment-content mb-5">
                                                                        <p>
                                                                            ${content.val()}
                                                                        </p>
                                                                    </div>
                                                                    <div class="feeling mt-5">
                                                                        <button class="btn btn-link btn-icon-left btn-slide-up btn-infinite like ml-2 like-comment" data-id="${response.id}">
                                                                            <i class="fa fa-thumbs-up"></i>
                                                                            لایک (<span class="count">0</span>)
                                                                        </button>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </li>
                    `
                );
                content.val('');
                setButtonLoading(btn, false, 'ارسال شد');
                $('.comment-response').addClass('d-none');
                $('.comment-count').text(function(_, txt) {
                    return 'نظر (' + (((txt.match(/\d+/) && parseInt(txt.match(/\d+/)[0])) || 0) + 1) + ')';
                });
                setTimeout(function() {
                    setButtonLoading(btn, false, 'ارسال نظر');
                }, 3000);
            },
            error: function(xhr, status, error) {
                console.log(error);
                setButtonLoading(btn, false, 'مشکلی پیش آمد');
                setTimeout(function() {
                    setButtonLoading(btn, false, 'ارسال نظر');
                }, 3000);
            }
        });
    });

    $('.like-comment').click(function(e) {
        e.preventDefault();

        let btn = $(this);
        let comment_id = btn.data('id');

        $.ajax({
            url: '/shop/comment_like/',
            type: 'PATCH',
            headers: {
                'X-CSRFToken': csrf_token
            },
            data: {
                'id': comment_id
            },
            success: function(response) {
                if (response.like) {
                    btn.children('.count').text(Number(btn.children('.count').text()) + 1);
                } else {
                    btn.children('.count').text(Number(btn.children('.count').text()) - 1);
                }
            },
            error: function(xhr, status, error) {
                console.log(error);

                if (xhr.status === 403) {
                    $('.login-toggle').click();
                }
            }
        });
    });

    $('.btn-suggestion-wishlist').click(function(e) {
        e.preventDefault();

        let btn = $(this);
        let pid = btn.data('id');

        btn.addClass('load-more-overlay loading');

        $.ajax({
            url: '/shop/like_handler/',
            type: 'PATCH',
            headers: {
                'X-CSRFToken': csrf_token
            },
            data: {
                'id': pid
            },
            success: function(response) {
                btn.removeClass('load-more-overlay loading');
                if (response.like) {
                    $('#like-icon-' + pid).css('color', 'red')
                } else {
                    $('#like-icon-' + pid).css('color', '');
                }
                let link = $('#suggestion-title-' + pid);
                themeparsi.Minipopup.init();
                themeparsi.Minipopup.open({
                    message: `محصول با موفقیت ${response.like ? 'به علاقه مندی ها اضافه شد' : 'از علاقه مندی ها حذف شد'}!`,
                    productClass: 'product-wishlist',
                    name: link.text(),
                    nameLink: link.attr('href'),
                    imageSrc: $('#image-' + pid).attr('srcset'),
                    imageLink: link.attr('href'),
                    // price: "۲۵۰,۰۰۰ تومان",
                    // count: 1,
                    actionTemplate: `<div class="action-group d-flex"><a href="${link.attr('href')}" class="btn btn-sm btn-outline btn-primary btn-rounded">مشاهده محصول</a></div>`
                });
            },
            error: function(xhr, status, error) {
                console.log(error);
                btn.removeClass('load-more-overlay loading');
                if (xhr.status === 401) {
                    $('.login-toggle').click();
                }
            }
        });
    });

    $('.btn-suggestion-compare').click(function(e) {
        e.preventDefault();

        let btn = $(this);
        let pid = btn.data('id')

        btn.addClass('load-more-overlay loading');
        let link = $('#suggestion-title-' + pid);

        $.ajax({
            url: '/account/dashboard/compare/action/',
            type: 'PATCH',
            headers: {
                'X-CSRFToken': csrf_token
            },
            data: {
                'id': pid,
                'action': 'update'
            },
            success: function(response) {
                btn.removeClass('load-more-overlay loading');
                themeparsi.Minipopup.init();
                themeparsi.Minipopup.open({
                    message: `محصول با موفقیت ${response.added ? 'به لیست مقایسه اضافه شد' : 'از لیست مقایسه حذف شد'}!`,
                    productClass: 'product-wishlist',
                    name: link.text(),
                    nameLink: link.attr('href'),
                    imageSrc: $('#image-' + pid).attr('srcset'),
                    imageLink: link.attr('href'),
                    // price: "۲۵۰,۰۰۰ تومان",
                    count: 1,
                    actionTemplate: '<div class="action-group d-flex"><a href="/account/dashboard/compare/" class="btn btn-sm btn-outline btn-primary btn-rounded">لیست مقایسه</a></div>'
                });
            },
            error: function(xhr, status, error) {
                console.log(error);
                btn.removeClass('load-more-overlay loading');
                if (xhr.status === 401) {
                    $('.login-toggle').click();
                } else if (xhr.status === 403) {
                    themeparsi.Minipopup.init();
                    themeparsi.Minipopup.open({
                        message: `لیست مقایسه شما پر است!`,
                        productClass: 'product-wishlist',
                        name: link.text(),
                        nameLink: link.attr('href'),
                        imageSrc: $('#image-' + pid).attr('srcset'),
                        imageLink: link.attr('href'),
                        // price: "۲۵۰,۰۰۰ تومان",
                        count: 1,
                        actionTemplate: '<div class="action-group d-flex"><a href="/account/dashboard/compare/" class="btn btn-sm btn-outline btn-primary btn-rounded">لیست مقایسه</a></div>'
                    });
                }
            }
        });
    });

    $('.btn-notify-me').click(function(e) {
        e.preventDefault();

        let btn = $(this);

        setButtonLoading(btn, true, 'در حال ثبت');

        $.ajax({
            url: '/shop/notify_me/',
            type: 'PATCH',
            headers: {
                'X-CSRFToken': csrf_token
            },
            data: {
                'id': product_id
            },
            success: function(response) {
                setButtonLoading(btn, false, response.added ? 'منتظر موجود شدن':'در صورت موجود شدن اطلاع بده');
                themeparsi.Minipopup.init();
                themeparsi.Minipopup.open({
                    message: response.added ? 'زمانی که این محصول موجود شد از طریق پیامک و ایمیل خبرسانی میشه':'از لیست خبررسانی حذف شد',
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
            }
        });
    });

    $('.size').click(function(e) {
        e.preventDefault();

        let value = $(this).text();
        let price = $('#product-actual-price')
        let discount = price.data('discount');
        let base_price = Number(discount) === -1 ? price.data('price'):discount;

        let final_price = Number(value) * Number(base_price);

        setTimeout(function() {
            $('#final-price').text(final_price.toLocaleString() + ' تومان');
        }, 10);
    });
});
