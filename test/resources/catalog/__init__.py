def assert_core_view(doc):
    assert doc.id == '5cd8328e-febe-3299-8e26-cf6ab2c07f0f'
    assert doc.title == \
        'Changes in tree reproductive traits reduce functional diversity in a fragmented Atlantic forest landscape'
    assert doc.type == 'journal'
    assert doc.source == 'PLoS ONE'
    assert doc.year == 2007
    assert doc.identifiers['doi'] == '10.1371/journal.pone.0000908'
    assert doc.link == 'https://www.mendeley.com/catalogue/5cd8328e-febe-3299-8e26-cf6ab2c07f0f/'
    #assert 'critical for the maintenance' in doc.abstract
    assert len(doc.authors) == 4
    assert doc.authors[1].first_name == 'Ariadna Valentina'
    assert doc.authors[1].last_name == 'Lopes'


def assert_bib_view(doc):
    assert doc.volume == '2'
    assert doc.issue == '9'
    assert not doc.editors


def assert_stats_view(doc):
    assert doc.reader_count > 0
    assert doc.reader_count_by_academic_status['Professor'] > 0
    assert doc.reader_count_by_subdiscipline['Psychology']['Psychology'] > 0
    assert doc.reader_count_by_country['United States'] > 0


def assert_all_view(doc):
    assert_core_view(doc)
    assert_bib_view(doc)
    assert_stats_view(doc)
