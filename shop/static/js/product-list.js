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
});