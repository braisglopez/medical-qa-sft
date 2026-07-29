# MIRAGE Pairwise Analysis: gemma_drugs

## Overall

| Total | Base acc | Tuned acc | Delta | Improved | Worsened | Net |
|---:|---:|---:|---:|---:|---:|---:|
| 7663 | 0.4926 | 0.4905 | -0.0021 | 458 | 474 | -16 |

## By Dataset

| Dataset | Base acc | Tuned acc | Delta | Improved | Worsened | Both correct | Both wrong | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| bioasq | 0.7071 | 0.6877 | -0.0194 | 5 | 17 | 420 | 176 | -12 |
| medmcqa | 0.4466 | 0.4449 | -0.0017 | 280 | 287 | 1581 | 2035 | -7 |
| medqa | 0.4745 | 0.4666 | -0.0079 | 71 | 81 | 523 | 598 | -10 |
| mmlu | 0.5712 | 0.5510 | -0.0202 | 52 | 74 | 548 | 415 | -22 |
| pubmedqa | 0.4880 | 0.5580 | +0.0700 | 50 | 15 | 229 | 206 | 35 |

## Examples

### bioasq

#### improved

- gold=A base=B tuned=A question=Is rilonacept effective for pericarditis?
- gold=A base=B tuned=A question=Is the apilimod inhibitor effective against SARS-CoV-2?
- gold=A base=B tuned=A question=Is there an upper limit on the functional fraction of the human genome?
- gold=B base=A tuned=B question=Do genes with monoallelic expression contribute proportionally to genetic diversity in humans?
- gold=B base=A tuned=B question=Do de novo truncating mutations in WASF1 cause cancer?

#### worsened

- gold=B base=B tuned=A question=Are Luminopsins a fusion proteins of luminol and Rhodopsin ?
- gold=B base=B tuned=A question=Is Wilson's disease described as an iron storage disease?
- gold=B base=B tuned=A question=Was prehospital transdermal glyceryl trinitrate effective for stroke in the RIGHT-2 trial?
- gold=A base=A tuned=B question=In twin-twin transfusion syndrome, are the twins identical?
- gold=A base=A tuned=B question=Is Mycobacterium abscessus a human pathogen?

#### both_correct

- gold=A base=A tuned=A question=Is PRP-40 regulation of microexons a conserved phenomenon?
- gold=A base=A tuned=A question=Is casimersen effective for the treatment of Duchenne muscular dystrophy?
- gold=B base=B tuned=B question=Is medical hydrology the same as Spa therapy?
- gold=A base=A tuned=A question=Is eteplirsen effective for the treatment of Duchenne muscular dystrophy?
- gold=A base=A tuned=A question=Does CIDEB mutation protect from liver disease?

#### both_wrong

- gold=B base=A tuned=A question=Can losartan reduce brain atrophy in Alzheimer's disease?
- gold=B base=A tuned=A question=Is deflazacort more efficient than prednisone/prednisolone for the treatment of Duchenne muscular dystrophy?
- gold=B base=A tuned=A question=Based on clinical trial data, can pioglitazone delay cognitive impairment for people at risk for Alzheimer's disease?
- gold=B base=A tuned=A question=Does silencing of SRRM4 promote microexon inclusion?
- gold=B base=A tuned=A question=Was erythropoietin effective for optic neuritis in the TONE trial?

### medmcqa

#### improved

- gold=A base=C tuned=A question=Which of the following statements is true regarding H I N1 Influenza?
- gold=B base=A tuned=B question=Diagnosis of the following ECG-
- gold=A base=B tuned=A question=A second-year PG resident tells you to perform an ABG of a patient. All of the following are true about performing an ABG except:
- gold=A base=C tuned=A question=A patient who was on ventilator and being ventilated for past few days, suddenly pulls out the endotracheal tube. What is the next step of management?
- gold=B base=C tuned=B question=Which of the following is not. true regarding myelopathy?

#### worsened

- gold=A base=A tuned=B question=Characteristic of venous blood flow of lower limb in duplex Doppler is?
- gold=D base=D tuned=C question=In Erythroblastosis fetalis not involved is –
- gold=D base=D tuned=C question=A 60 years old male presented with fever, chills and dysuria. Patient was hospitalized in emergency for 5 days. PSA level was 7.4. Next best step in this patient:
- gold=B base=B tuned=C question=Incorporation of peripheral seal in an impression is necessary to obtain;
- gold=C base=C tuned=B question=A patient has seasonal allergic rhinitis and is on terfenadine. He develops cardiac arrhythmias after a course of antibiotics. Which of the following antibiotic could have been given:

#### both_correct

- gold=A base=A tuned=A question=Which of the following is not true for myelinated nerve fibers:
- gold=C base=C tuned=C question=A 29 yrs old woman with a pregnancy of 17 week has a 10 years old boy with down syndrome. She does not want another down syndrome kid; best advice to her is
- gold=A base=A tuned=A question=Concentration of tropicamide:
- gold=B base=B tuned=B question=A blue new born presents with cyanosis. The X–ray chest reveal oligaemic lung field and normal sized heart. Most likely diagnosis is –
- gold=B base=B tuned=B question=27.	The lateral spread of dental caries is facilitated mostly  by the

#### both_wrong

- gold=A base=B tuned=B question=Which of the following is not true about glomerular capillaries')
- gold=C base=A tuned=A question=Axonal transport is:
- gold=A base=B tuned=B question=Low insulin to glucagon ratio is seen in all of these except:
- gold=B base=C tuned=A question=Which of the following are not a branch of external carotid Aery in Kiesselbach's plexus.
- gold=A base=D tuned=B question=Heavy forces on periodontal ligament causes:

### medqa

#### improved

- gold=B base=C tuned=B question=Two weeks after undergoing an emergency cardiac catherization with stenting for unstable angina pectoris, a 61-year-old man has decreased urinary output and malaise. He has type 2 diabetes mellitus and osteoarthritis of the hips. Prior to admission, his medications were insulin and naproxen. He was also started on aspirin, clopidogrel, and metoprolol after the coronary intervention. His temperature is 38°C (100.4°F), pulse is 93/min, and blood pressure is 125/85 mm Hg. Examination shows mottled, reticulated purplish discoloration of the feet. Laboratory studies show:
Hemoglobin count 14 g/dL
Leukocyte count 16,400/mm3
Segmented neutrophils 56%
Eosinophils 11%
Lymphocytes 31%
Monocytes 2%
Platelet count 260,000/mm3
Erythrocyte sedimentation rate 68 mm/h
Serum
Urea nitrogen 25 mg/dL
Creatinine 4.2 mg/dL
Renal biopsy shows intravascular spindle-shaped vacuoles. Which of the following is the most likely cause of this patient's symptoms?"
- gold=C base=D tuned=C question=A 65-year-old man is brought to the emergency department 30 minutes after the onset of acute chest pain. He has hypertension and asthma. Current medications include atorvastatin, lisinopril, and an albuterol inhaler. He appears pale and diaphoretic. His pulse is 114/min and blood pressure is 130/88 mm Hg. An ECG shows ST-segment depressions in leads II, III, and aVF. Laboratory studies show an increased serum troponin T concentration. The patient is treated for acute coronary syndrome and undergoes percutaneous transluminal coronary angioplasty. At the time of discharge, echocardiography shows a left ventricular ejection fraction of 58%. In addition to aspirin, which of the following drugs should be added to this patient's medication regimen?
- gold=B base=A tuned=B question=A 37-year-old-woman presents to her primary care physician requesting a new form of birth control. She has been utilizing oral contraceptive pills (OCPs) for the past 8 years, but asks to switch to an intrauterine device (IUD). Her vital signs are: blood pressure 118/78 mm Hg, pulse 73/min and respiratory rate 16/min. She is afebrile. Physical examination is within normal limits. Which of the following past medical history statements would make copper IUD placement contraindicated in this patient?
- gold=C base=B tuned=C question=A 4-year-old boy is brought to the emergency department because of severe abdominal pain and bilious vomiting for 6 hours. He has not had bowel movements in the past 24 hours. He appears ill. His temperature is 37.8°C (100°F) and pulse is 122/min. Examination shows a distended abdomen. There is tenderness to palpation in the lower abdomen; guarding and rebound tenderness are present. Bowel sounds are decreased. An x-ray of the abdomen shows dilated loops of bowel. He has been accompanied by his 14-year-old brother. The surgeon recommends an emergency laparotomy. The parents are away visiting friends and cannot be reached. Which of the following is the most appropriate next best step in management?
- gold=C base=D tuned=C question=A 26-year-old woman is brought to the emergency department 20 minutes after being involved in a high-speed motor vehicle collision in which she was a restrained passenger. On arrival, she is lethargic and incoherent. She has severe facial lacerations and is in respiratory distress. Her pulse is 130/min, respirations are 29/min, and blood pressure is 90/58 mm Hg. Pulse oximetry on room air shows an oxygen saturation of 70%. Examination shows multiple facial lacerations. There is dullness to percussion and decreased breath sounds over the left lung base. Abdominal examination shows diffuse tenderness with no guarding or rebound. Bowel sounds are normal. The remainder of the examination shows no abnormalities. Her hemoglobin concentration is 12.1 g/dL. An x-ray of the chest shows a fractured left second rib, depression of the left mainstem bronchus, deviation of the nasogastric tube to the right, and a widened mediastinum. Which of the following is the most likely diagnosis?

#### worsened

- gold=C base=C tuned=B question=A 30-year-old African American woman comes to the physician for the evaluation of a dry cough and chest discomfort for the past 3 days. During this period, the patient has had headaches, muscle aches, joint pain, fever, and chills. Ten days ago, she was hiking with her family in Mississippi. The patient has asthma that is treated with an albuterol inhaler. Her mother has a lung disease treated with methotrexate. The patient has smoked one pack of cigarettes daily for the past 10 years. Her temperature is 38°C (100.4°F). Physical examination shows slight wheezes throughout both lung fields. Laboratory studies and urinalysis are positive for polysaccharide antigen. Bronchoalveolar lavage using silver/PAS-staining shows macrophages filled with a dimorphic fungus with septate hyphae. Which of the following is the most likely cause of this patient's symptoms?
- gold=A base=A tuned=C question=A 67-year-old male is seen by neurology after he was noticed to be speaking strangely by his family. After acute treatment with tissue plasminogen activator (tPA), the patient is able to recover most of his speech. Subsequent neurologic exam finds that the patient is fluent while speaking and is able to comprehend both one and two step instructions. Noticeably the patient remains unable to complete tasks involving verbal repetition. Residual damage to which of the following structures is most likely responsible for this patient's syndrome?
- gold=A base=A tuned=C question=A healthy 19-year-old man presents to his primary care provider complaining of painless “blisters” in his mouth. He reports that he noticed a white film on his tongue and the sides of his mouth 2 days ago while brushing his teeth. The film was easily brushed off. He also complains of a bitter metallic taste in his mouth but otherwise denies pain, burning, dysphagia, or hoarseness. He is otherwise healthy and takes no medications. He is a competitive swimmer and has had 8 sexual partners in the past year. He intermittently uses barrier protection. On exam, he is well-appearing and in no acute distress. His oral examination demonstrates patches of white pseudomembranes that can be wiped away to reveal erythematous mucosa. A medication with which of the following mechanisms of action is most appropriate in this patient?
- gold=C base=C tuned=A question=A 25-year-old male involved in a knife fight presents with a penetrating wound to the chest. The patient is unconscious and cannot provide any further history. Vitals show a temperature of 37-0°C (98.6°F), blood pressure of 85/55 mm Hg, pulse of 115/min, respirations of 19/min, and oxygen saturation of 92% on room air. On physical examination, the patient is diaphoretic and unresponsive. Extremities are pale and cool. There is a 3-inch long penetrating wound between the 3rd and 4th intercostal space on the left side of the chest, which is bleeding profusely. Transthoracic echocardiography reveals a full thickness penetrating injury to the right ventricular free wall. There are no apparent injuries to any coronary arteries or major branches. The patient is intubated and aggressive fluid resuscitation is initiated, including a blood transfusion. Which of the following is the best definitive surgical approach to take in this patient?
- gold=C base=C tuned=A question=A previously healthy 30-year-old woman comes to the physician for the evaluation of pain during sexual intercourse for 6 months. She also reports frequent episodes of crampy pelvic pain that starts one day before menses and lasts for 7 days. Her symptoms are not relieved with pain medication. Menses occur at regular 28-day intervals and last 5 days. Her last menstrual period was 2 weeks ago. She is sexually active with her husband. She uses a combined oral contraceptive pill. Her vital signs are within normal limits. Physical examination shows rectovaginal tenderness. Cervical and urethral swabs are negative. Transvaginal ultrasonography shows no abnormalities. Which of the following is the most appropriate next step in management?

#### both_correct

- gold=D base=D tuned=D question=A 67-year-old man with transitional cell carcinoma of the bladder comes to the physician because of a 2-day history of ringing sensation in his ear. He received this first course of neoadjuvant chemotherapy 1 week ago. Pure tone audiometry shows a sensorineural hearing loss of 45 dB. The expected beneficial effect of the drug that caused this patient's symptoms is most likely due to which of the following actions?
- gold=B base=B tuned=B question=A 35-year-old man comes to the physician because of itchy, watery eyes for the past week. He has also been sneezing multiple times a day during this period. He had a similar episode 1 year ago around springtime. He has iron deficiency anemia and ankylosing spondylitis. Current medications include ferrous sulfate, artificial tear drops, and indomethacin. He works as an elementary school teacher. His vital signs are within normal limits. Visual acuity is 20/20 without correction. Physical examination shows bilateral conjunctival injection with watery discharge. The pupils are 3 mm, equal, and reactive to light. Examination of the anterior chamber of the eye is unremarkable. Which of the following is the most appropriate treatment?
- gold=A base=A tuned=A question=A 23-year-old woman comes to the physician because she is embarrassed about the appearance of her nails. She has no history of serious illness and takes no medications. She appears well. A photograph of the nails is shown. Which of the following additional findings is most likely in this patient?
- gold=D base=D tuned=D question=A 72-year-old man comes to the physician because of a 2-month history of fatigue and worsening abdominal pain. During this period, he also has excessive night sweats and shortness of breath on exertion. Over the past 3 months, he has had a 5.6-kg (12-lb) weight loss. He had a myocardial infarction 3 years ago. He has hypertension, diabetes mellitus, and chronic bronchitis. His medications include insulin, aspirin, lisinopril, and an albuterol inhaler. He has smoked half a pack of cigarettes for the past 45 years. Vital signs are within normal limits. The spleen is palpated 6 cm below the left costal margin. Laboratory studies show:
Hemoglobin 6.4 g/dL
Mean corpuscular volume 85 μm3
Leukocyte count 5,200/mm3
Platelet count 96,000/mm3
A blood smear is shown. Bone marrow aspiration shows extensive fibrosis and a few scattered plasma cells. A JAK 2 assay is positive. Which of the following is the most appropriate next step in management?"
- gold=B base=B tuned=B question=A 59-year-old overweight woman presents to the urgent care clinic with the complaint of severe abdominal pain for the past 2 hours. She also complains of a dull pain in her back with nausea and vomiting several times. Her pain has no relation with food. Her past medical history is significant for recurrent abdominal pain due to cholelithiasis. Her father died at the age of 60 with some form of abdominal cancer. Her temperature is 37°C (98.6°F), respirations are 15/min, pulse is 67/min, and blood pressure is 122/98 mm Hg. Physical exam is unremarkable. However, a CT scan of the abdomen shows a calcified mass near her gallbladder. Which of the following diagnoses should be excluded first in this patient?

#### both_wrong

- gold=B base=A tuned=A question=A junior orthopaedic surgery resident is completing a carpal tunnel repair with the department chairman as the attending physician. During the case, the resident inadvertently cuts a flexor tendon. The tendon is repaired without complication. The attending tells the resident that the patient will do fine, and there is no need to report this minor complication that will not harm the patient, as he does not want to make the patient worry unnecessarily. He tells the resident to leave this complication out of the operative report. Which of the following is the correct next action for the resident to take?
- gold=D base=A tuned=A question=A 39-year-old woman is brought to the emergency department because of fevers, chills, and left lower quadrant pain. Her temperature is 39.1°C (102.3°F), pulse is 126/min, respirations are 28/min, and blood pressure is 80/50 mm Hg. There is blood oozing around the site of a peripheral intravenous line. Pelvic examination shows mucopurulent discharge from the cervical os and left adnexal tenderness. Laboratory studies show:
Platelet count 14,200/mm3
Fibrinogen 83 mg/mL (N = 200–430 mg/dL)
D-dimer 965 ng/mL (N < 500 ng/mL)
When phenol is applied to a sample of the patient's blood at 90°C, a phosphorylated N-acetylglucosamine dimer with 6 fatty acids attached to a polysaccharide side chain is identified. A blood culture is most likely to show which of the following?"
- gold=D base=B tuned=B question=A 39-year-old man presents to the emergency department because of progressively worsening chest pain and nausea that started at a local bar 30 minutes prior. The pain radiates to the epigastric area. He has a 5-year history of untreated hypertension. He has smoked 1 pack of cigarettes daily for the past 5 years and started abusing cocaine 2 weeks before his emergency room visit. The patient is diaphoretic and in marked distress. What should be the first step in management?
- gold=C base=D tuned=A question=A 68-year-old male comes to the physician for evaluation of right flank pain. He has a history of diabetes and peripheral artery disease. His blood pressure is 160/90 mm Hg. Physical examination shows abdominal tenderness and right flank tenderness. An ultrasound shows dilation of the right ureter and renal pelvis. Which of the following is the most likely underlying cause of this patient's condition?
- gold=D base=C tuned=C question=A 24-year-old G2P1 woman at 39 weeks’ gestation presents to the emergency department complaining of painful contractions occurring every 10 minutes for the past 2 hours, consistent with latent labor. She says she has not experienced vaginal discharge, bleeding, or fluid leakage, and is currently taking no medications. On physical examination, her blood pressure is 110/70 mm Hg, heart rate is 86/min, and temperature is 37.6°C (99.7°F). She has had little prenatal care and uses condoms inconsistently. Her sexually transmitted infections status is unknown. As part of the patient’s workup, she undergoes a series of rapid screening tests that result in the administration of zidovudine during delivery. The infant is also given zidovudine to reduce the risk of transmission. A confirmatory test is then performed in the mother to confirm the diagnosis of HIV. Which of the following is most true about the confirmatory test?

### mmlu

#### improved

- gold=B base=D tuned=B question=Which muscles are normally active during quiet inspiration?
- gold=D base=A tuned=D question=Oxygenated blood is carried to the heart by which of the following structures?
- gold=A base=D tuned=A question=The mucosa of the upper larynx is innervated by the
- gold=A base=D tuned=A question=The infraorbital nerve
- gold=B base=C tuned=B question=When an emergency opening into the airway is required, the cricothyroid membrane should be pierced immediately

#### worsened

- gold=B base=B tuned=A question=A "dished face" profile is often associated with
- gold=B base=B tuned=C question=Laryngoscopic examination of the vocal folds after suspected recurrent laryngeal nerve damage usually shows that the vocal fold on the injured side is tensed and in an intermediate position between adduction and abduction. This is because
- gold=D base=D tuned=A question=Which of the following structures accompany the oesophagus through the diaphragm?
- gold=D base=D tuned=A question=Which of the following best describes the location where the carotid pulse can be found?
- gold=C base=C tuned=A question=The head of the sixth rib articulates with

#### both_correct

- gold=A base=A tuned=A question=Which of the following best describes the structure that collects urine in the body?
- gold=C base=C tuned=C question=Which of the following structures is derived from ectomesenchyme?
- gold=B base=B tuned=B question=Which of the following describes the cluster of blood capillaries found in each nephron in the kidney?
- gold=A base=A tuned=A question=Which of the following anatomical regions of abdomen lies just distal to the sternum?
- gold=B base=B tuned=B question=Which of the following best describes the human body's defense mechanism against environmental bacteria?

#### both_wrong

- gold=A base=C tuned=C question=A lesion causing compression of the facial nerve at the stylomastoid foramen will cause ipsilateral
- gold=B base=A tuned=A question=A patient suffers a broken neck with damage to the spinal cord at the level of the sixth cervical vertebra.
- gold=C base=B tuned=B question=The palatine processes begin to fuse at
- gold=D base=B tuned=A question=Primary motor cortex activity results in
- gold=D base=C tuned=C question=You notice that your patient's submandibular lymph nodes are enlarged. You would look for potential infection sites in the

### pubmedqa

#### improved

- gold=A base=B tuned=A question=Is portable ultrasonography accurate in the evaluation of Schanz pin placement during extremity fracture fixation in austere environments?
- gold=A base=C tuned=A question=Proof of concept study: does fenofibrate have a role in sleep apnoea syndrome?
- gold=A base=C tuned=A question=Differentiation of nonalcoholic from alcoholic steatohepatitis: are routine laboratory markers useful?
- gold=A base=C tuned=A question=The Prevalence of Incidentally Detected Idiopathic Misty Mesentery on Multidetector Computed Tomography: Can Obesity Be the Triggering Cause?
- gold=A base=C tuned=A question=Fast foods - are they a risk factor for asthma?

#### worsened

- gold=B base=B tuned=A question=Do African American women require fewer calories to maintain weight?
- gold=B base=B tuned=A question=The use of audit to identify maternal mortality in different settings: is it just a difference between the rich and the poor?
- gold=B base=B tuned=A question=Do foreign bodies migrate through the body towards the heart?
- gold=B base=B tuned=A question=Is it necessary to insert a nasobiliary drainage tube routinely after endoscopic clearance of the common bile duct in patients with choledocholithiasis-induced cholangitis?
- gold=B base=B tuned=A question=Does the treatment of amblyopia normalise subfoveal choroidal thickness in amblyopic children?

#### both_correct

- gold=A base=A tuned=A question=Is anorectal endosonography valuable in dyschesia?
- gold=A base=A tuned=A question=Is there a connection between sublingual varices and hypertension?
- gold=A base=A tuned=A question=Is the affinity column-mediated immunoassay method suitable as an alternative to the microparticle enzyme immunoassay method as a blood tacrolimus assay?
- gold=A base=A tuned=A question=Does a physician's specialty influence the recording of medication history in patients' case notes?
- gold=A base=A tuned=A question=Locoregional opening of the rodent blood-brain barrier for paclitaxel using Nd:YAG laser-induced thermo therapy: a new concept of adjuvant glioma therapy?

#### both_wrong

- gold=A base=C tuned=B question="Occult" posttraumatic lesions of the knee: can magnetic resonance substitute for diagnostic arthroscopy?
- gold=A base=B tuned=B question=Do patients with rheumatoid arthritis established on methotrexate and folic acid 5 mg daily need to continue folic acid supplements long term?
- gold=A base=B tuned=B question=Assessing Patient Reported Outcomes Measures via Phone Interviews Versus Patient Self-Survey in the Clinic: Are We Measuring the Same Thing?
- gold=A base=C tuned=B question=Assessment of appropriate antimicrobial prescribing: do experts agree?
- gold=A base=C tuned=B question=Is it appropriate to implant kidneys from elderly donors in young recipients?

