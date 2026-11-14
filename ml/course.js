// The whole course, in order. A unit counts as written once its lessons are in the course_content table.
// Priorities, in order: overall understanding, medical statistics, the maths of the models (optional depth), basic Python.
window.COURSE_PARTS = [
  {
    title: 'Part 1: Foundations',
    units: [
      { n: 1, title: 'What a model is', about: 'Rules, parameters, loss, honest testing, and the map of an AF prediction model.' },
      { n: 2, title: 'Data: signals, tables and time', about: 'How waveforms, printed values and repeated visits become numbers. Kinds of variables, scaling, and missing values.' },
      { n: 3, title: 'Describing data', about: 'Mean, median, spread, percentiles, histograms, the Heart Rate Score, correlation, and change over time.' }
    ]
  },
  {
    title: 'Part 2: Medical statistics',
    units: [
      { n: 4, title: 'Chance and uncertainty', about: 'Why two samples differ, standard error, confidence intervals, and resampling.' },
      { n: 5, title: 'Testing a claim', about: 'Hypotheses, p-values, the two kinds of error, power, sample size, and the cost of testing many aims.' },
      { n: 6, title: 'Study design and bias', about: 'Cohorts, case-control studies and trials. Confounding, selection, immortal time, prevalent cases, left truncation.' },
      { n: 7, title: 'Measuring association', about: 'Risk, odds, relative and absolute differences, number needed to treat, adjustment, and why association is not cause.' },
      { n: 8, title: 'Diagnostic tests and risk scores', about: 'Sensitivity, specificity, predictive values, base rates, likelihood ratios, and the ROC curve.' }
    ]
  },
  {
    title: 'Part 3: How models work, and what else could do the job',
    units: [
      { n: 9, title: 'The simplest models', about: 'Linear and logistic regression: your baseline model, how to read its coefficients, and how to keep it from overfitting.' },
      { n: 10, title: 'How a model learns', about: 'Slopes, gradient descent, learning rate, overfitting, regularisation, and tuning.' },
      { n: 11, title: 'Testing honestly', about: 'Cross-validation, holdout, leakage, external and prospective validation, discrimination, calibration, and usefulness.' },
      { n: 12, title: 'Models for tables', about: 'Decision trees, random forests, gradient boosting, nearest neighbours. When a simpler model beats a deep one.' },
      { n: 13, title: 'Neural networks', about: 'Neurons, layers, activation functions, and how errors flow backward to train them.' },
      { n: 14, title: 'Reading waveforms', about: 'Convolution, filters, the EGM encoder and embeddings. Rivals: hand-made features, recurrent networks, transformers.' },
      { n: 15, title: 'Learning without labels', about: 'Self-supervised and contrastive learning, autoencoders, pretrained models, clustering, and compressing many numbers into few.' },
      { n: 16, title: 'Patient timelines', about: 'Recurrent networks, attention and transformers, irregular visits, landmarks. Rival: summary features fed to a table model.' },
      { n: 17, title: 'Time-to-event analysis', about: 'Censoring, Kaplan-Meier curves, the log-rank test, hazards, Cox models, and hazard ratios.' },
      { n: 18, title: 'Survival models and their rivals', about: 'Competing risks, left truncation, discrete-time models, deep survival models, survival forests, and the C-index.' }
    ]
  },
  {
    title: 'Part 4: Judging the project and changing it',
    units: [
      { n: 19, title: 'When things go wrong', about: 'Missing data, rare outcomes, disagreement between reviewers, differences between manufacturers and sites, explaining a prediction.' },
      { n: 20, title: 'An AF prediction model, end to end', about: 'Every part read together, each with the alternatives you could swap in and what each swap would cost.' },
      { n: 21, title: 'Reading and reporting a prediction study', about: 'A critical-appraisal checklist, reporting standards, subgroup fairness, and what reviewers ask.' },
      { n: 22, title: 'Beyond this project', about: 'A first look at image models, language models and other kinds of AI, and how they relate to what you built. Part 5 goes deeper.' }
    ]
  },
  {
    title: 'Part 5: Going deeper (optional)',
    units: [
      { n: 23, title: 'Vectors and matrices', about: 'The language models are written in: lists of numbers, dot products, matrices, and what a layer does to its input.' },
      { n: 24, title: 'Derivatives and gradient descent by hand', about: 'Slopes of curves, the chain rule, and backpropagation worked through on paper.' },
      { n: 25, title: 'Probability for models', about: 'Random variables, the common distributions, expected value, and the probability rules models rely on.' },
      { n: 26, title: 'Likelihood and Bayesian thinking', about: 'Likelihood, maximum likelihood, priors and posteriors, and why logistic regression and cross-entropy loss are the same idea.' },
      { n: 27, title: 'Regression modelling in depth', about: 'Interactions, curved effects and splines, shrinkage, checking a model, and how many predictors your events can support.' },
      { n: 28, title: 'Causal inference', about: 'Prediction versus cause: causal diagrams, confounders and colliders, propensity scores, and emulating a target trial.' },
      { n: 29, title: 'Images and convolutional networks', about: 'How networks read images: two-dimensional filters, pooling, well-known architectures, and medical imaging.' },
      { n: 30, title: 'Attention and transformers', about: 'Attention worked step by step, position, and why transformers now read signals, text and images.' },
      { n: 31, title: 'Large language models', about: 'Tokens, next-word prediction, pretraining and fine-tuning, prompting, retrieval, and why they make things up.' },
      { n: 32, title: 'Foundation models in medicine', about: 'Models pretrained on huge datasets and adapted to many tasks: ECG and imaging examples, how they are judged, regulation, and limits.' }
    ]
  }
];
window.COURSE_MAP = window.COURSE_PARTS.flatMap(part => part.units);
