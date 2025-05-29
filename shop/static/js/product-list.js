$(document).ready(function() {
    $(window).scrollTop(0);

    if(window.location.search) {
        $('.remove-filters').removeClass('d-none');
    }

    $('.apply-filters').click(function(e) {
        let selected_brands = []
        $('.brand-side').each(function() {
            if($(this).hasClass('active')) {
                selected_brands.push($(this).data('brand'))
            }
        });

        let selected_volumes = [];
        $('.volume-select').each(function() {
            if($(this).hasClass('active')) {
                selected_volumes.push($(this).data('volume'));
            }
        });

        let selected_smells = [];
        $('.smell-select').each(function() {
            if($(this).hasClass('active')) {
                selected_smells.push($(this).data('value'));
            }
        });

        let selected_seasons = [];
        $('.season-select').each(function() {
            if($(this).hasClass('active')) {
                selected_seasons.push($(this).data('value'));
            }
        });

        let selected_tastes = [];
        $('.taste-select').each(function() {
            if($(this).hasClass('active')) {
                selected_tastes.push($(this).data('value'));
            }
        });

        let selected_nature = [];
        $('.nature-select').each(function() {
            if($(this).hasClass('active')) {
                selected_nature.push($(this).data('value'));
            }
        });

        let selected_durability = [];
        $('.durability-select').each(function() {
            if($(this).hasClass('active')) {
                selected_durability.push($(this).data('value'));
            }
        });

        let selected_spread = [];
        $('.spread-select').each(function() {
            if($(this).hasClass('active')) {
                selected_spread.push($(this).data('value'));
            }
        });

        let selected_gender = [];
        $('.gender-select').each(function() {
            if($(this).hasClass('active')) {
                selected_gender.push($(this).data('value'));
            }
        });

        if (
            selected_brands.length === 0 &&
            selected_volumes.length === 0 &&
            selected_smells.length === 0 &&
            selected_spread.length === 0 &&
            selected_seasons.length === 0 &&
            selected_tastes.length === 0 &&
            selected_nature.length === 0 &&
            selected_durability.length === 0 &&
            selected_gender.length === 0
        ) {
            location.reload();
        }


        $.ajax({
            url: '/shop/products/list/',
            type: 'GET',
            data: {
                'brands': selected_brands,
                'volumes': selected_volumes,
                'smells': selected_smells,
                'spreads': selected_spread,
                'seasons': selected_seasons,
                'tastes': selected_tastes,
                'nature': selected_nature,
                'durability': selected_durability,
                'gender': selected_gender,
            },
            success: function(response) {
                // console.log(response);
                $('.product-wrapper').replaceWith(response);
                $('.pagination').addClass('d-none');
                $('.sidebar-close').click();
                $(window).scrollTop(0);
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });

    $('.active-filter').click(function(e) {
        e.preventDefault();
        $('.remove-filters').removeClass('d-none');
    });

    $(document).on('click', '.btn-list-wishlist', function(e) {
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
                let link = $('#list-title-' + pid);
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

    $(document).on('click', '.btn-list-compare', function(e) {
        e.preventDefault();

        let btn = $(this);
        let pid = btn.data('id')

        btn.addClass('load-more-overlay loading');
        let link = $('#list-title-' + pid);

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
});