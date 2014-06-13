# Build scripts require pip and virtualenv.
# See http://virtualenv.readthedocs.org/

# By default, runs a full prep/generate cycle.
# During routine hacking, you will usually not need to re-run prep.
default: prep generate

prep:
	./prep.sh

generate: clean
	./generate.sh

package:
	tar --exclude='.DS_Store' --exclude='.git' -czf docset.tgz goog.docset

# Deletes generated files.
clean:
	rm -f \
	  goog.docset/icon.png \
	  goog.docset/Contents/Info.plist \
	  goog.docset/Contents/Resources/docSet.dsidx

# Deletes all files that should not be present in a fresh checkout.
distclean: clean
	rm -Rf PYTHON_ENV \
	  `find . -name '*~'` \
	  goog.docset/Contents/Resources/Documents
	mkdir -p goog.docset/Contents/Resources/Documents
