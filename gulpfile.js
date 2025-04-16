'use strict';
const path = require('path');
const gulp = require('gulp');
const sass = require('gulp-sass')(require('sass'));
const sourcemaps = require('gulp-sourcemaps');

const PROJECT_DIR = path.resolve(__dirname);
const SASS_FILES = `${PROJECT_DIR}/sass/**/*.scss`;
const OUTPUT_CSS = `${PROJECT_DIR}/static`;

gulp.task('sass', function (done) {
  return gulp.src(SASS_FILES)
    .pipe(sourcemaps.init())
    .pipe(sass({
      outputStyle: 'expanded',
      includePaths: ['node_modules']
    }).on('error', sass.logError))
    .pipe(sourcemaps.write('./sourcemaps', {includeContent: false}))
    .pipe(gulp.dest(OUTPUT_CSS))
    .on('end', done);
});

gulp.task('sass:watch', function (done) {
  gulp.watch(SASS_FILES, gulp.series('sass'));
  done();
});

gulp.task('default', gulp.series('sass'));
