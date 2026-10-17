# Simple presentation script

Read only the paragraphs under each slide heading. Aim for 6-8 minutes, with short pauses when showing the charts.

## Slide 1 — Research question

My project looks at a simple question: why do people feel worried about the economy, even when some economic numbers look better?

I look at unemployment, inflation, economic growth, and consumer sentiment. Consumer sentiment means how people feel about their finances and the economy. I also study economic news and Reddit posts.

There are several possible reasons for the gap. Families may still face high costs. News may shape how people see the economy. Or our model may miss something important.

I compare these explanations without assuming that the media is biased. The research cutoff is October 14, 2026.

## Slide 2 — Checking the data

First, I checked the supplied spreadsheet against official data.

For example, the spreadsheet gives August PCE inflation as about 3.01 percent. My calculation from the official price index gives about 3.42 percent. PCE is a measure of consumer prices.

I also checked when each number became available. Third-quarter GDP had not been released by my cutoff, so I left it out.

October consumer sentiment was available, but it was still a preliminary result. I kept the missing unemployment value as missing.

The main rule is simple: a prediction should only use information available at that time.

## Slide 3 — How the predictions work

Next, I tested the models over time.

For each month, I used the economic data available before that month began. I collected 202 monthly data snapshots, starting in 2010.

GDP stays quarterly. I use the latest released quarter until a new number becomes available.

I compared predictions with actual consumer sentiment over 105 months, from 2018 through September 2026.

One simple model is called persistence. It uses the latest available consumer sentiment value as the next prediction.

This gives us a benchmark. A more complicated model should do better than this simple approach.

## Slide 4 — Which model works better?

This chart shows prediction errors. Lower is better.

The persistence model has an error of 4.75 points. The model using only economic indicators has a much larger error: 14.10 points.

Adding recent consumer sentiment lowers that error to 5.19. Adding household-related measures gives an error of 5.54.

So, in this test, the simplest benchmark performs best.

This does not mean the economy is unimportant. It means that our economic model does not predict people's feelings very well.

We should not automatically blame the media for what the model fails to explain.

## Slide 5 — The October sentiment gap

Here I compare actual sentiment with the model predictions.

October's preliminary sentiment value is 46.3. The economic-only model predicts a much higher value, leaving a gap of minus 26.55 points.

When I add recent sentiment, the gap becomes much smaller: minus 6.81 points.

The ranges shown on this slide describe uncertainty. The actual value is inside both models' prediction ranges.

The key point is that the gap changes a lot when we change the model.

So, the gap alone cannot show that people are irrational or that media coverage caused their pessimism.

## Slide 6 — News classification

I collected 316 news headlines and Reddit post titles, including national and local news.

For 300 texts, I used labels from Claude and DeepSeek. I temporarily treat each set as a separate reference answer.

I compare two methods: Naive Bayes, which learns word patterns, and a dictionary method, which checks positive and negative words.

This chart shows F1 scores. Higher is better. The dictionary scores higher under both AI references.

This suggests that a model trained on company news may struggle with household and economic news.

These scores depend on the AI reference. They are not independent human validation.

## Slide 7 — Does news improve the forecast?

I also tested a longer news sentiment index from the San Francisco Fed.

Adding this index slightly improves the economic-only model. Its error falls from 14.10 to 13.92.

But for the model that already includes recent consumer sentiment, the error rises slightly, from 5.19 to 5.23.

Overall, I do not find a clear, stable improvement across the full test period.

This is a historical comparison. I could not confirm which version of the news index was available at every past prediction date.

These results also do not tell us whether news causes changes in consumer sentiment.

## Slide 8 — Practical takeaway

For financial forecasting and risk monitoring, my main takeaway is to check the model before using a sentiment gap as a warning signal.

Compare it with a simple benchmark. Look at the uncertainty range. Check when the input data became available.

The dashboard makes these checks easier. We can switch models and see how the forecast and gap change.

My project finds that both the prediction model and the text classification method matter.

The current evidence does not show that media bias caused low consumer sentiment. More data and independent validation would help answer that question.

Thank you.

### Optional dashboard demo — do not read these instructions aloud

Replace the two dashboard sentences on Slide 8 with this demonstration. Keep it to about 20 seconds.

Switch to the dashboard. Change **Forecast model** from **Economic** to **Economic plus persistence**.

Say: “Here, changing the model changes the gap from about minus 26.5 to minus 6.8. This shows why model choice matters.”

Return to the final slide and finish the script.

### Sources — for reference, not for reading aloud

The report contains full sources. Slides 2-3 use official BLS, BEA, Michigan, FRED and ALFRED data. Slides 4-5 use the saved forecast results. Slide 6 uses `results/ai_reference_evaluation.json`. Slide 7 uses `results/news_index_comparison.json` and the San Francisco Fed news sentiment index.
