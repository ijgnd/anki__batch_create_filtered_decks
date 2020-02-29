I would use this add-on only with the "Anki 2.1 scheduler (beta)" (formerly laelled 
"experimental scheduler") which as of Anki 2.1.20 you must enable from the 
main window->Tools->Preferences. The default scheduler has this
limitation mentioned in the manual, https://apps.ankiweb.net/docs/manual.html#home-decks:

> In the current implementation, if you create, rebuild, empty or delete a filtered deck while 
cards are still in learning, they will be turned back into new cards. In the case of failed 
reviews in relearning, any remaining relearning steps will be skipped. This has been fixed in the experimental scheduler.

A complementary add-on is "Rebuild All & Empty All".

&nbsp;

- `mirror all decks as filtered`-`selected by/order`: You need to use numbers 0-8: 
    - 0: Oldest seen first
    - 1: Random
    - 2: Increasing intervals
    - 3: Decreasing intervals
    - 4: Most lapses
    - 5: Order added
    - 6: Order due
    - 7: Latest added first
    - 8: Relative overdueness

&nbsp;

If you can't copy the following sample configs you can also view (and copy) them from 
[this webpage](https://github.com/ijgnd/anki__batch_create_filtered_decks/blob/master/src/config.md).

&nbsp;

To mirror all decks as filtered decks and have due cards in order created you could try this:

    {
        "mirror all decks as filtered": [
            {
                "additional search term": "is:due",
                "max cards": 9999,
                "reschedule based on answers": true,
                "selected by/order": 5,
                "parent deck name": "0::Order added"
            }
        ]
    }

&nbsp;

To mirror all decks as filtered decks and have due cards with intervals over 4 days sorted by their
relative overdueness you could try this:

    {
        "mirror all decks as filtered": [
            {
                "additional search term": "is:due  prop:ivl>=4",
                "max cards": 9999,
                "reschedule based on answers": true,
                "selected by/order": 8,
                "parent deck name": "0::Relative overdueness"
            }
        ]
    }

&nbsp;

For a method from TheAnking's video [Anki:How to Miss a Day (making up skipped days...)](https://youtu.be/UXgck-g0nQA?t=747) which was originally
[suggested on reddit](https://www.reddit.com/r/medicalschoolanki/comments/amj7iw/an_efficient_method_for_catching_up_on_anki/) you could try: 

    {
        "mirror all decks as filtered": [
            {
                "additional search term": "is:due prop:due>-3",
                "max cards": 9999,
                "reschedule based on answers": true,
                "selected by/order": 1,
                "parent deck name": "0::recent__do_all_of_those_every_day"
            },
            {
                "additional search term": "is:due prop:due<=-3",
                "max cards": 100,
                "reschedule based on answers": true,
                "selected by/order": 8,
                "parent deck name": "0::old_overdues__sorted_by_overdueness"
            }
        ]
    }

`prop:due>-3` is used to also fetch buried siblings that were due on the days before.