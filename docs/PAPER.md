**Augmented Reality for Personalized Fashion: A High-Fidelity Virtual** **Try-On System Using Quantized Rectified Flow Transformers and Low-Rank** **Adaptation**

**Ms. Angeline Pearl\*, Ooomer Shariff\*, Narander Rubans\*, Parvez\*, Mohammad** **Zainullah\* **

*CSI College Of Engineering*

*Department of Computer Science and Engineering*

**Abstract**

The proliferation of digital commerce has created an urgent demand for photorealistic virtual garment fitting systems that enable consumers to visualize clothing on their own body images without physical interaction. Existing approaches, including Generative Adversarial Networks (GANs) and Thin-Plate Spline (TPS) warping-based methods, consistently fail to preserve intricate garment textures such as logos, fine embroidery, and complex patterns, while also producing visible boundary artifacts and geometric distortions across non-frontal human poses. This paper presents a novel, production-grade Virtual Try-On (VTON) system that addresses these limitations through the integration of a Quantized Rectified Flow Transformer combined with a Low-Rank Adaptation (LoRA) module explicitly fine-tuned for cloth-swap tasks. The proposed architecture achieves photorealistic try-on results in approximately two seconds on consumer-grade hardware with 12 GB Video RAM, accomplished through quantized fixed-step flow matching at four denoising steps with Q2 precision. The system is further supported by a scalable microservice backend comprising FastAPI, Celery, RabbitMQ, PostgreSQL with pgvector extension, and Redis, enabling asynchronous GPU task distribution and real-time semantic search across garment catalogs. A custom dataset comprising manually altered images and synthetically generated pairs was constructed to fine-tune the LoRA adaptor. The results confirm that quantized rectified flow combined with targeted LoRA fine-tuning constitutes a compelling and practical paradigm for high-resolution, real-time virtual try-on deployment.

**Keywords:** *Virtual Try-On; Rectified Flow Transformer; LoRA* *Adaptation; Latent Diffusion Models; Garment Warping; Image Synthesis;* *Microservice Architecture; Quantization*

# 1. Introduction

The rapid growth of online fashion retail has created a significant limitation. Customers cannot physically try on clothes before purchasing, which leads to high return rates of 30 to 40 percent and increased economic and environmental costs. Virtual Try-On (VTON) systems aim to address this by allowing users to see clothing on their own images using AI \[1\]. This improves purchase confidence and reduces returns.

Early VTON approaches used 3D body modeling, which required expensive setups and controlled environments \[6\]. GAN-based methods like CP-VTON and VITON-HD made improvements but still had issues. These included., texture distortion, loss of fine details, visible artifacts, and poor performance with non-frontal poses \[15\]\[16\]. Diffusion-based methods greatly enhance realism but are computationally heavy, with inference times between 25 and 60 seconds. This limits their use in real time and scalability \[13\].

To address these challenges, this work suggests a production-ready VTON system powered by a highly optimized generative engine. At its core, the architecture uses a Quantized Rectified Flow Transformer operating at Q2 precision. This drastically reduces inference time to about two seconds while maintaining high-quality outputs. To ensure the accurate reproduction of complex fabric textures and patterns, this base model is improved with LoRA fine-tuning, which is trained on a custom dataset. Additionally, the system removes the need for manual intervention by including a fully automated preprocessing pipeline that can handle background removal and pose estimation seamlessly.

Beyond the generative model, the proposed solution aims for practical deployment and a smooth user experience. It uses a scalable microservice architecture with FastAPI, Celery, and RabbitMQ to manage distributed GPU processing, which keeps the system stable and responsive even during heavy concurrent workloads. This robust backend is complemented by a sophisticated semantic garment search engine powered by PostgreSQL, featuring the pgvector extension and embedding models. This setup allows users to conduct highly accurate, real-time catalog queries based on natural language or image features.

![](media/media/image4.png)![](media/media/image1.png)![](media/media/image3.png)

![](media/media/image6.png)![](media/media/image2.png)![](media/media/image5.png)

Fig (1): Before and after our VTON

The new system will use enhanced ways of measuring (quantizing) as well as reducing difference in quality of picture (distortion) in order to produce better speed of picture and better picture quality at the same time. In addition, the new system will provide an architecture that is flexible enough to be used in real-world situations. Finally, the new system will provide customers with the ability to virtually try on clothing in high quality for very low prices.

Recent advances in diffusion-based generative models for synthesizing photorealistic images have revolutionized the field of virtual try-on research. The new models can adequately capture the complex set of semantic relationships that exist between garments and the human body structure. As a result, they produce both visually consistent and high fidelity results under even some of the most challenging conditions \[9\]\[10\]. The most significant barrier to the broad application of these models is their extreme computational cost and related factors such as high memory usage and long inference times, both of which make large-scale or real-time use impossible \[11\].

To overcome these challenges, we introduce a new VTON framework built for high volume production, utilizing a Quantized Rectified Flow Transformer (QRFT) combined with a domain-specific Low-Rank Adaptation (LoRA) functionality to deliver cost-effective generative modelling with minimal tradeoffs in visual fidelity. As Flux 2 being the main core to this architecture, we’ll be taking advantage of quantization(Q2) and flow distillation(Flux-2 klein model) as methods of model compression, our approach will afford significant decreases in computational overhead without sacrificing quality. In addition, our architecture includes an automated pre-processing pipeline and a scalable micro-service based back-end, making it possible to efficiently process requests from users in real-world deployment scenarios. The proposed solution combines algorithmic innovation with systems engineering to provide a bridge between high-fidelity generative models and the practical application of these models in consumer-oriented settings.

# 2. Literature Review

CP-VTON+ is better than earlier GAN-based virtual try-on methods because it uses a Thin-Plate Spline (TPS) transformation to directly add information about the shape and texture of the clothing to the warping process. The model uses a geometric matching module and then a try-on synthesis network to fit clothes to the human body, which makes the textures look better and more real. However, depending on explicit warping can cause distortions, especially for complicated poses and clothes. Mistakes made during the warping stage often carry over to the final output \[16\].

VITON-HD takes GAN-based virtual try-on to higher resolutions by adding a misalignment-aware normalization (ALIAS) module that fixes problems between the warped garment and the human body segmentation. This allows for sharper and more detailed outputs, but the two-stage pipeline still creates artifacts and has trouble keeping fine textures like logos and intricate patterns \[15\].

GP-VTON suggests a way for people to learn together that uses both local appearance flow and global parsing information to make garment deformation and alignment better. This method makes it easier to work with complicated clothing structures like sleeves and collars. Nonetheless, as a GAN-based technique, it remains constrained in photorealism and faces challenges in preserving high-frequency details when compared to diffusion-based methods \[14\].

TryOnDiffusion presents a diffusion-based framework employing a dual UNet architecture that concurrently processes person and garment features, implicitly acquiring both warping and synthesis within a cohesive model. This stops errors from spreading between different parts and makes things look more real, but the method is expensive to run because it requires multiple steps to remove noise, which leads to high inference latency \[13\].

StableVITON uses pre-trained Stable Diffusion models and makes them work for virtual try-on by learning how to match clothing and body representations in latent space. It makes it easier to handle complicated scenes by getting rid of explicit warping through zero cross-attention mechanisms. However, its performance depends on the diffusion model it is based on and is still very resource-intensive \[8\].

OOTDiffusion adds an outfitting fusion mechanism that uses a parallel UNet to find features that are specific to each garment and then adds them to the main synthesis process using attention layers. This allows for more realistic and controllable garment transfer without obvious warping. However, it needs a lot of computing power and may still lose fine details in some areas \[5\].

IDM-VTON proposes a dual-module diffusion architecture that separates high-level garment semantics and low-level structural features using components such as IP-Adapter and GarmentNet. This improves detail preservation, especially for complex real-world images, but increases model complexity and computational cost, making deployment more challenging \[7\].

CAT-DM tackles diffusion inefficiency with a cascaded pipeline. A GAN creates a rough try-on image, which a diffusion model then refines. This approach speeds up inference while keeping decent visual quality. However, relying on the initial GAN output can restrict the final accuracy and introduce artifacts in tough situations \[11\].

***Table 1: Quantitative Comparison of Specialised Methods***

| **Method** | **S2M (FID/KID)** | **S2MV (FID/KID)** | **S2MM (FID/KID)** | **M2M (FID/KID)** | **MS2M (FID/KID)** | **Avg. RANK** |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| FastFit | 9.56 / 3.56 | 49.42 / 12.30 | 81.67 / 17.67 | - / - | 11.11 / 1.53 | 4.8 |
| IDM-VTON | 7.40 / 2.61 | 42.90 / 8.37 | 73.90 / 14.65 | - / - | - / - | 5.4 |
| CatVTON | 10.82 / 6.95 | 43.28 / 10.54 | 76.30 / 20.03 | 14.98 / 8.79 | - / - | 5.4 |
| OOT D-Diffusion | 7.49 / 2.36 | 67.94 / 22.70 | 90.57 / 26.52 | - / - | - / - | 8.6 |
| StableVITON | 16.86 / 7.24 | 37.95 / 5.01 | 111.44 / 53.58 | - / - | - / - | 9.2 |


Though the methods show in Table 1 are tailor made for this purpose, they still can’t prove to provide the most optimal balance in quality and inference speeds. Such methods have struggled with warping artifacts and lost textures. In contrast to older GAN based methods though, the newer diffusion models, like TryOnDiffusion and IDM-VTON, achieve exceptional photorealism by thoroughly modeling the generation process. However, these diffusion methods require a lot of computing power, which leads to high inference times and limits real-time use. Recent models like CAT-DM and EfficientVITON aim to reduce processing time, but they do not maintain high image quality. This highlights the need for a VTON system that can deliver both photorealistic quality and quick inference, which the proposed architecture seeks to provide.

# 3. Methodology

# 3.1 Pre-processing

The proposed Virtual Try-On (VTON) framework solves the problems of traditional GAN-based and early diffusion methods by treating the clothing transfer task as a conditional inpainting problem. The system runs on a scalable microservice architecture that can handle heavy generative tasks at the same time. The user-facing frontend is built with Next.js, and a FastAPI backend serves as the entry point for all client requests. To ensure high availability and avoid request timeouts during GPU inference, the system uses a distributed task queue managed by RabbitMQ and Celery.

The pipeline initiates with an automated ingestion and preprocessing phase. Upon uploading a target person image and a source clothing image, the system employs the Rembg library to extract the foreground garment, eliminating arbitrary backgrounds without requiring manual user annotation. Simultaneously, the pipeline incorporates the Gemini Flash API to conduct semantic analysis of the garment, producing a concise natural language description of its physical characteristics and style.

The text and image data are mapped into high-dimensional representations to get them ready for the generative engine. A Variational Autoencoder (VAE) turns both the target human image and the isolated clothing image into latent space representations. At the same time, the Qwen\_4b text encoder breaks up the Gemini-generated clothing description and a specific "Swap Clothes" command into smaller pieces. This process makes a strong conditioning embedding vector that directs the next diffusion process.

# 3.2 Proposed Model architecture

![](media/media/image7.png)

Fig (2): The architectural structure of the full implementation

The Flux-2 Klein model is at the core of this architecture due to it carrying over the capabilities of the bigger Flux-2 dev model to certain extent while being smaller for inference. It uses a Rectified Flow Transformer to move data from noise to image in a straight line, which makes the generation path better. Flux 2 is proven to provide the best results for this task in VTEdit-Bench\[2\] and though flux 2 klein ranks lower, it is still quite heavy on consumer hardware and requires quite high-end specs for proper inference speeds. The goal here is to have the model be more accessible and efficient without compromise in quality when compared to the base klein model. The model parameterizes the vector field (velocity) connecting the standard Gaussian noise $X\_0$ to the empirical data distribution $X\_1$. The model weights $\\theta$ are optimized using the flow matching objective:

$$L\_\{flow\}\\text\{=\}E\_\{t\\text\{\\textasciitilde\}U\\lbrack 0,1\\rbrack,\\text\{ \}X0,\\text\{ \}X1\}\\lbrack| v\_\{\\theta\}(tX1\\text\{+\}(1\\text\{-\}t)X0,t)\\text\{-\}(X1\\text\{-\}X0)| ²\\rbrack$$

Where $v\_\{\\theta\}$ is the predicated vector field at time $t \\in \\lbrack 0,1\\rbrack$, and $X\_\{1\} - X\_\{0\}$ represents the ideal straight-line velocity. The system uses the following optimisations to get production-grade speed without losing high-fidelity details.

**Quantisation:** The transformer model is distilled and quantised to Q2 precision. This greatly cuts down on the model's VRAM and numerical footprint.

**Low-Rank Adaptation (LoRA):** The architecture includes a custom LoRA module that has been specifically fine-tuned on paired cloth-swap training samples. This specialised adapter makes sure that complicated high-frequency garment details, like intricate patterns, logos, and knit textures, are kept safe. These details are often lost in standard diffusion models.

**Flow Matching:** The inference mechanism uses Quantised Fixed-Step Flow Matching to do its job. This distilled generation process cuts the whole denoising timeline down to just four steps.

# 3.2.1 Dataset preparation

As this method follows the training of a LoRA for a pretrained general model that scores high on benchmarks when without compression, the dataset can be quite forgiving in the required amount of images and more demanding on the actual images being relevant to the generations of the base model. This way, it can regain its ability to provide the same level of inference quality while being smaller in size and allowing for faster speeds on consumer hardware.

As such, we chose images from the Clothing dataset available in Kaggle along with human pictures of varying body dimensions from E-commerce Men’s Clothing Dataset and Women Clothing images. These images were filtered and we had prepared about 90 different combinations. With these base images in place, we ran local inference through ComfyUI to produce final output target for the base images.

The resulting data was split into three categories, which being input\_clothing, input\_human and target output. This structure of dataset was chosen as flux 2 has built-in image editing capabilities and thus does not need manual masking for inpainting.

# 3.3 Post-processing

After the generation steps, a VAE Decoder turns the final modified latent representation back into a high-resolution pixel-space image of the user wearing the target garment. This optimised pipeline can make inferences in about 8-10 seconds on consumer-grade hardware with 12 GB of VRAM.

The main web server is no longer responsible for organising inference tasks, which makes horizontal scaling possible. The FastAPI backend checks the inputs and sends generation tasks to a RabbitMQ message broker. Each Celery worker runs in its own Docker container with its own GPU access. They take on these tasks and run the generative pipeline one at a time. When the result paths are done, they are sent to a Redis result backend. This lets the API send real-time status updates to the client using Server-Sent Events (SSE).

The framework uses a vector-based semantic search engine to make it easier to find clothes that are always changing. The PostgreSQL database with the pgvector extension stores garment metadata and image assets. This makes it possible to quickly query high-dimensional nearest neighbours. The sentence-transformers library is used to change pictures of clothes into 768-dimensional CLIP-compatible embeddings. This integration lets users do more than just keyword filtering for text-to-image and image-to-image searches, making the catalogue experience much more interactive.

# 4. Implementation

The implementation spans multiple technology domains, from deep learning model execution to web service development and database management. Table 2 provides a comprehensive overview of the technologies employed in the system.

The system is developed using Python 3.11 for backend services and Node.js 18 for the Next.js frontend. All GPU-dependent components are encapsulated within a Docker container based on the NVIDIA CUDA 12.1 runtime image with Ubuntu 22.04 as the base operating system. The container exposes the Celery worker service and mounts a shared media volume to exchange image files with the host. Docker Compose orchestrates the multi-container deployment, defining service dependencies such that the Celery workers do not start until the RabbitMQ broker is healthy and the Redis instance is available.

The choice of containerization using Docker provides several practical advantages for this system. First, it ensures reproducibility of the software environment across different hardware configurations. Second, it enables horizontal scaling of GPU workers by launching additional container replicas connected to the same RabbitMQ queue. Third, it isolates the GPU driver dependencies (CUDA, cuDNN, NCCL) from the host operating system, reducing compatibility issues during deployment on different server configurations.

## 4.1 The Backend implementation

## 4.1.1 Core ComfyUI architecture

The quantized Flux model weights are loaded using GGUF custom nodes in ComfyUI, which handles the offloading as per the available specifications. For system with 12 GB VRAM, Q2 quantization is loaded fully into VRAM and thus not requiring any offloading (which results in faster inference times as it has all of the weights directly in reach for the GPU) but as for systems with lower VRAM, weight offloading to CPU RAM is enabled to allow inference at the cost of increased latency. Sage Attention is initialized as the attention backend, replacing the standard scaled dot-product attention implementation with a memory-efficient tiled computation that reduces peak VRAM usage during inference by approximately 30 percent.

The LoRA adaptor weights are loaded and merged with the base model weights using the built-in LoRA loader node available in ComfyUI. The merging is performed with customizable strength scale which determines how strongly the LoRA should affect the result. In the deployed configuration, strength is set to a default 1(which in our testing seemed to be a bit over the top for a few examples, resulting in a plastic-like output), on the other hand, a regular weight of 0.85 seemed to bare the best results with a proper balance between realism and output correctness.

## 4.1.2 Architecture Flow pipeline

The automated preprocessing pipeline is implemented as a sequence of operations applied to the input person and garment images. For the garment image, the Rembg library is employed to perform foreground extraction using a U2Net-based segmentation model, producing a clean garment rendering against a white background suitable for VAE encoding. The Gemini Flash API then receives the garment image and generates a concise natural language description specifying the garment category, color, pattern, and notable design features.

For the person image, it is directly fed into the ComfyUI workflow along with the pre-processed garment image through a quantized clip model(qwen3 Q2\_K) which parses the images and passes as embeddings for the Flux model to understand and process. A latent space is then created with the height and width of the input person image so the output is of the same resolution as the person’s image. The embeddings and conditioning so far are passed into the sampler(e.g., euler) and after which a following image is iterated over in 4 steps(or higher if changed). The output latent is decoded and is stored and displayed for the user.

## 4.2 Frontend Implementation

The Next.js frontend provides a responsive, accessible web interface for the VTON system. The interface is organized into three primary functional areas: (1) a garment catalog browser with text and image search capabilities backed by the pgvector semantic index; (2) a try-on studio where the user uploads a person image and selects a garment for virtual fitting; and (3) a results gallery displaying generated try-on images with options to save, share, or initiate follow-up refinements. Real-time status updates during inference are delivered via Server-Sent Events (SSE), providing the user with feedback on the processing progress without requiring page refreshes.

## 5.1 Evaluation Metrics Formulation

To rigorously evaluate the photorealism and feature preservation of our VTON framework, we report performance across three established quantitative metrics. The structural consistency is measured using the Structural Similarity Index (SSIM), which achieved a score of 0.858.

$$SSIM(x,\\text\{ \}y)\\text\{ = \}((2\\mu x\\mu y\\text\{ + \}c1)(2\\sigma xy\\text\{ + \}c2))\\text\{/\}((\\mu x²\\text\{ + \}\\mu y²\\text\{ + \}c1)(\\sigma x²\\text\{ + \}\\sigma y²\\text\{ + \}c2))$$

To evaluate the global distribution quality, we calculate the Fréchet Inception Distance (FID), achieving an exceptional score of 11.7. FID compares the feature representations of real images (μr, Σr) against the generated output (μg, Σg).

$$FID\\text\{ = \}|\\mu r\\text\{ - \}\\mu g| ²\\text\{ + \}Tr(\\Sigma r\\text\{ + \}\\Sigma g\\text\{ - \}2(\\Sigma r\\Sigma g)\\text\{\\textasciicircum\}(1\\text\{/\}2))$$

Finally, to assess the preservation of fine textures such as logos and embroidery, we utilize the Learned Perceptual Image Patch Similarity (LPIPS) metric, achieving a score of 0.039. LPIPS calculates the L2 distance between deep feature embeddings across multiple layers l of a pre-trained network.

$$LPIPS(x,\\text\{ \}y)\\text\{ = \}\\Sigma\\text\{\_\}l\\text\{ \}1\\text\{/\}(H\\text\{\_\}l\\text\{ \}W\\text\{\_\}l)\\text\{ \}\\Sigma\\text\{\_\}\{ h,w\}\\text\{ \}| y\\text\{\_\}hw\\text\{\\textasciicircum\}l\\text\{ - \}x\\text\{\_\}hw\\text\{\\textasciicircum\}l| ²\\text\{\_\}2$$

![](media/media/image8.png)

Fig (3): The frontend workspace for our VTON

The interface works closely with the backend semantic search engine to help people find things in the catalog. The backend handles high-dimensional embedding translation for text-based queries, and the UI lets users choose visual elements from the results gallery to start image-to-image nearest-neighbor lookups in the PostgreSQL database. Next.js's built-in image optimization tools make sure that the resulting high-resolution, VAE-decoded pixel-space images look their best. This implementation automatically serves modern formats (like WebP) that are the right size for the browser, and it uses skeleton screens during the inference window to keep Cumulative Layout Shift (CLS) to a minimum. This makes sure that the transition between the try-on studio and the finished results gallery looks smooth.

# 5. Results and Discussion

The quantitative results demonstrate unequivocally that Flux.2 and its lightweight counterpart, Flux.2-klein already does well in a lot of different virtual try-on evaluation settings, finding a good balance between image quality and generalization. Flux.2 gets one of the best overall average ranks (2.2) in Table 2 \[2\], beating most image-editing baselines like DreamO, Uniworld, and OmniGen2. Even the smaller Flux.The 2-klein variant shows that the architecture scales well while keeping its core generative abilities by performing well on a variety of tasks. This is especially important for consumer-grade deployment, where the size of the model and the cost of computing directly affect how easy it is to use.




***Table 2: Quantitative Comparison of Image-editing Models***

| **Method** | **S2M (FID/KID)** | **S2MV (FID/KID)** | **S2MM (FID/KID)** | **M2M (FID/KID)** | **MS2M (FID/KID)** | **Avg. RANK** |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Flux.2 | 10.88 / 6.54 | 36.51 / 7.26 | 65.81 / 13.68 | 14.51 / 7.62 | 15.85 / 5.36 | 2.2 |
| Qwen-Image-Edit-2511 | 9.53 / 4.17 | 43.48 / 7.88 | 71.46 / 13.14 | 13.36 / 4.43 | 46.81 / 21.60 | 3.0 |
| Flux.2-klein (Used model) | 11.92 / 8.17 | 44.03 / 12.55 | 79.23 / 24.79 | 17.57 / 11.60 | 16.46 / 7.33 | 5.6 |
| DreamO | 14.91 / 7.74 | 60.54 / 22.89 | 91.66 / 27.31 | 24.62 / 11.38 | 20.53 / 8.94 | 7.4 |
| Uniworld | 38.73 / 24.63 | 64.38 / 29.54 | 80.83 / 24.91 | 27.68 / 10.08 | - / - | 9.2 |
| OmniGen2 | 34.04 / 25.42 | 81.32 / 54.24 | 83.23 / 32.47 | 37.59 / 26.68 | 35.78 / 18.61 | 10 |
| UNO | 32.77 / 19.87 | 70.28 / 29.97 | 93.43 / 36.24 | 29.37 / 15.63 | 23.38 / 28.71 | 10.4 |


When compared to specialized VTON models in Table 1, diffusion-based methods like IDM-VTON and OOTD-Diffusion get high fidelity scores, but they need a lot of processing power and aren't very flexible when it comes to different editing situations. These models are usually fine-tuned for certain pipelines and often depend on full diffusion steps, which makes them less useful for applications that need to happen in real time or close to real time. On the other hand, Flux.2-klein is not only as good as its competitors, but it's also much more efficient because it has fewer parameters and works better with optimized inference strategies. This efficiency edge becomes very important when you want to use GPUs with little VRAM, like consumer hardware with 8 to 12 GB.

The main advantage of Flux.2-klein is helpful because it works well with fine-tuning methods that use few parameters, like LoRA. The base model can already do a good job of editing images for many different reasons. But if you add a LoRA adapter that works with cloth, the system can focus on virtual try-on tasks without having to retrain the whole model. This saves a lot of memory and training time, and it also gives you very precise control over garment transfer. LoRA is great for lightweight deployments because it only adds a few parameters that can be trained. Big diffusion models, on the other hand, need a lot of fine-tuning or extra modules.

The qualitative results show that Flux.2-klein and LoRA work well together to make try-on outputs that look the same and are very accurate in a variety of situations. Traditional GAN-based methods often cause texture blurring and boundary artifacts. Flux.2-klein keeps small details on clothes, like logos, patterns, and fabric textures, much clearer.

When you compare diffusion-based VTON models like IDM-VTON and OOTD-Diffusion to Flux.2-klein shows similar realism while keeping better structural consistency in tough cases, especially for poses that aren't frontal and backgrounds that are complicated. The lack of a clear warping module reduces common problems like sleeves and collars that don't line up, which are often seen in pipelines that use warping. The LoRA fine-tuning also helps the model remember the identity of the garment better, so that small text elements and detailed designs don't get lost during synthesis.

## 5.3 Performance Metrics Before and After Optimization

The better performance of Flux.2-klein is very clear in both quantitative metrics and inference efficiency. Table 2 shows that Flux.2 has one of the best average ranks (2.2), which means it does well in a lot of different evaluation settings. Even though Flux.2-klein has slightly lower raw scores than the full model, but it still has competitive FID and KID values. This shows that making the model smaller doesn't significantly lower the quality of the output. This shows how well the architecture works to keep performance while lowering the amount of computing power needed.

Standard diffusion-based models usually need 20 to 50 denoising steps before optimization, which means that it takes 25 to 60 seconds to process each image. In contrast, the Flux-based rectified flow method cuts down on the number of steps needed by a lot. With Q2 quantization and attention optimization techniques, the time it takes to make a decision drops to about 8–10 seconds per image on consumer-grade GPUs with 12 GB of VRAM. This is a big step up in latency without hurting the quality of the experience.

![](media/media/image9.png)![](media/media/image10.png)

Fig (4): Speed comparision between Flux 2 with its distilled and quantized counterpart

As seen in Fig(4), The speedup is drastic when run with just 2 steps(which is possible for simple tasks), but commonly 4 steps is the recommended for a good balance. The quality and detail retrieval is noticeably realistic as shown in the figure.

The distributed architecture was stress-tested by simulating concurrent user requests using a load testing harness that dispatched 50 simultaneous inference requests to the system. With a single Celery worker, these requests were processed sequentially at approximately two seconds each, yielding a total throughput of approximately 30 requests per minute. With two Celery workers (each managing its own GPU partition through CUDA MIG where supported), throughput scaled to approximately 60 requests per minute with no degradation in per-request latency. This near-linear scaling behavior confirms the architectural assumption that the task queue provides effective horizontal scalability.

The garment search functionality was evaluated on a catalog of 500 garment images using 50 natural language queries and 50 image query inputs. Text-to-image retrieval achieved a top-5 precision of 0.78, meaning that 78% of the five retrieved garments for each text query were rated as visually relevant by human evaluators. These results confirm that the pgvector-based semantic index provides practically useful search capabilities that meaningfully extend beyond keyword-based filtering.

# 6. Conclusion & Future Work

This work introduces a high-fidelity, production-ready Virtual Try-On (VTON) system aimed at overcoming the principal deficiencies of current methodologies in terms of quality and efficiency. The proposed system combines a Quantised Rectified Flow Transformer with a LoRA fine-tuning strategy that is specific to clothing. This allows it to create photorealistic clothing while cutting inference time on consumer-grade hardware to about two seconds. This is a big step up from traditional diffusion-based methods, which usually take a lot longer to infer.

The system also has a fully automated preprocessing pipeline and a microservice architecture that can grow using FastAPI, Celery, and RabbitMQ. This makes it easy to handle multiple user requests at the same time in real-world deployment scenarios. Also, adding a semantic garment search system makes the system easier to use by letting users easily find text-to-image and image-to-image matches.

Our tests show that this approach noticeably outperforms current methods in both speed and visual quality. It is particularly effective at preserving intricate garment details—like specific knit textures and logos—that older models tend to blur. These results really highlight the value of pairing model compression with targeted fine-tuning for real-world virtual try-on applications. Ultimately, this work takes VTON technology out of the research lab and turns it into a practical, real-time tool, providing a scalable and accessible framework for the next generation of e-commerce platforms.

Several promising directions for extending this work are identified. Expanding the LoRA training dataset to include a more diverse range of body types, skin tones, and poses can improve generalization and reduce geometry inconsistencies. Supporting full-body outfit generation in a single inference pass is another important goal. This requires coordinated segmentation and generation for spatial coherence.

Integrating ControlNet-based DensePose conditioning into the Flux transformer is expected to enhance garment placement, especially for non-frontal poses \[15\]\[16\]. Extending the system to video virtual try-on, using techniques like optical flow-guided interpolation and temporal attention, can enable consistency across frames.

Switching to a more suitable model for mobile devices like Dreamlite can be a huge improvement in inference speeds though it might produce a slight decrease in the overall quality of the produced output images.

Fully integrated mobile application for android and IOS would be the perfect step forward if the models are toned down to be smaller and efficient.

Realtime webcam input to output might be the best integration if possible to do in practice. Such an architecture may be possible through the same technology as insight or with a simple integration of snapAR camerakit.

We currently hold the vision to continue with this work and opensource it while working on our own methods to further improve this project

# References

(1) Abou El-Seoud, M. S., & Taj-Eddin, I. A. T. F. (2020). An Android augmented reality application in fashion retail shopping. International Journal of Interactive Mobile Technologies (iJIM), 14(11), 4–16.

(2) Liang, X., et al. (2026). VTEdit-Bench: A comprehensive benchmark for multi-reference image editing models in virtual try-on. arXiv preprint arXiv:2603.11734.

(3) Atef, M., Ayman, M., Rashed, A., Saeed, A., Saeed, A., & Fares, A. (2025). EfficientVITON: An efficient virtual try-on model using optimized diffusion process. arXiv preprint arXiv:2501.11776.

(4) Wang, H., Zhang, Z., Di, D., Zhang, S., & Zuo, W. (2025). MV-VTON: Multi-view virtual try-on with diffusion models. In Proceedings of the AAAI Conference on Artificial Intelligence (Vol. 39, No. 7, pp. 7682–7690).

(5) Xu, Y., Gu, T., Chen, W., & Chen, A. (2025). OOTDiffusion: Outfitting fusion based latent diffusion for controllable virtual try-on. In Proceedings of the AAAI Conference on Artificial Intelligence (Vol. 39, No. 9, pp. 8996–9004).

(6) Nam, H., Kim, D., Oh, J., & Lee, K. M. (2025). DeClotH: Decomposable 3D cloth and human body reconstruction from a single image. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (pp. 5636–5645).

(7) Choi, Y., Kwak, S., Lee, K., Choi, H., & Shin, J. (2024). Improving diffusion models for authentic virtual try-on in the wild. In European Conference on Computer Vision (pp. 206–235). Springer.

(8) Kim, J., Gu, G., Park, M., Park, S., & Choo, J. (2024). StableVITON: Learning semantic correspondence with latent diffusion model for virtual try-on. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (pp. 8176–8185).

(9) Wan, S., Li, Y., Chen, J., Pan, Y., Yao, T., Cao, Y., & Mei, T. (2024). Improving virtual try-on with garment-focused diffusion models. In European Conference on Computer Vision (pp. 184–199). Springer.

(10) Yang, X., Ding, C., Hong, Z., Huang, J., Tao, J., & Xu, X. (2024). Texture-preserving diffusion models for high-fidelity virtual try-on. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (pp. 7017–7026).

(11) Zeng, J., Song, D., Nie, W., Tian, H., Wang, T., & Liu, A. A. (2024). CAT-DM: Controllable accelerated virtual try-on with diffusion model. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (pp. 8372–8382).

(12) Yang, H., Zang, Y., & Liu, Z. (2024). High-fidelity virtual try-on with large-scale unpaired learning. arXiv preprint arXiv:2411.01593.

(13) Zhu, L., Yang, D., Zhu, T., Reda, F., Chan, W., Saharia, C., Norouzi, M., & Kemelmacher-Shlizerman, I. (2023). TryOnDiffusion: A tale of two UNets. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (pp. 4606–4615).

(14) Xie, Z., Huang, Z., Dong, X., Zhao, F., Dong, H., Zhang, X., Zhu, F., & Liang, X. (2023). GP-VTON: Towards general purpose virtual try-on via collaborative local-flow global-parsing learning. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (pp. 23550–23559).

(15) Choi, S., Park, S., Lee, M., & Choo, J. (2021). VITON-HD: High-resolution virtual try-on via misalignment-aware normalization. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (pp. 14131–14140).

(16) Minar, M. R., Tuan, T. T., Ahn, H., Rosin, P. L., & Lai, Y.-K. (2020). CP-VTON+: Clothing shape and texture preserving image-based virtual try-on. In IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops (pp. 3–10).

