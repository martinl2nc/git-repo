<?php
/**
 * Plugin Name: Show Post ID
 * Description: A simple plugin to display the current Post ID using the [show_post_id] shortcode.
 * Version: 1.0
 * Author: Antigravity
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Exit if accessed directly
}

function spi_show_post_id_shortcode() {
	return get_the_ID();
}
add_shortcode( 'show_post_id', 'spi_show_post_id_shortcode' );
