'use strict';
const path = require('path');
const gulp = require('gulp');
const sass = require('gulp-sass');
const sourcemaps = require('gulp-sourcemaps');

const PROJECT_DIR = path.resolve(__dirname);
const SASS_FILES = `${PROJECT_DIR}/sass/**/*.scss`;
const OUTPUT_CSS = `${PROJECT_DIR}/static`;

gulp.task('sass', function () {
  return gulp.src(SASS_FILES)
    .pipe(sourcemaps.init())
    .pipe(sass({
      outputStyle: 'expanded'
    }).on('error', sass.logError))
    .pipe(sourcemaps.write('./sourcemaps'))
    .pipe(gulp.dest(OUTPUT_CSS));
});

gulp.task('sass:watch', function () {
  gulp.watch(SASS_FILES, ['sass']);
});

gulp.task('default', ['sass']);
