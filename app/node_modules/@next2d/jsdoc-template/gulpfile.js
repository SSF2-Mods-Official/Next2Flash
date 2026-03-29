const gulp     = require("gulp");
const cleanCSS = require("gulp-clean-css");
const rename   = require("gulp-rename");

/**
 * @description StyleSheetをまとめてminifyして出力
 * @return {*}
 * @public
 */
const buildStyleSheet = () =>
{
    return gulp
        .src("src/styles/*.css")
        .pipe(cleanCSS())
        .pipe(rename({ "extname": ".min.css" }))
        .pipe(gulp.dest("static/styles/"));
};

/**
 * @description ファイルを監視、変更があればビルドしてlocal serverを再読込
 * @return {void}
 * @public
 */
const watchFiles = () =>
{
    gulp
        .watch("src/styles/*.css")
        .on("change", gulp.series(buildStyleSheet));
};

exports.default = gulp.series(
    buildStyleSheet,
    watchFiles
);

exports.build = gulp.series(buildStyleSheet,);
