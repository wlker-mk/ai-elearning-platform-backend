-- CreateTable
CREATE TABLE "user_profiles" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "firstName" TEXT NOT NULL,
    "lastName" TEXT NOT NULL,
    "phoneNumber" TEXT,
    "dateOfBirth" TIMESTAMP(3),
    "profileImageUrl" TEXT,
    "coverImageUrl" TEXT,
    "bio" TEXT,
    "website" TEXT,
    "linkedin" TEXT,
    "github" TEXT,
    "twitter" TEXT,
    "facebook" TEXT,
    "country" TEXT,
    "city" TEXT,
    "timezone" TEXT NOT NULL DEFAULT 'UTC',
    "language" TEXT NOT NULL DEFAULT 'en',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "user_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "students" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "studentCode" TEXT NOT NULL,
    "points" INTEGER NOT NULL DEFAULT 0,
    "level" INTEGER NOT NULL DEFAULT 1,
    "experiencePoints" INTEGER NOT NULL DEFAULT 0,
    "streak" INTEGER NOT NULL DEFAULT 0,
    "maxStreak" INTEGER NOT NULL DEFAULT 0,
    "lastActivityDate" TIMESTAMP(3),
    "totalCoursesEnrolled" INTEGER NOT NULL DEFAULT 0,
    "totalCoursesCompleted" INTEGER NOT NULL DEFAULT 0,
    "totalLearningTime" INTEGER NOT NULL DEFAULT 0,
    "totalCertificates" INTEGER NOT NULL DEFAULT 0,
    "preferredCategories" TEXT[],
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "students_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "instructors" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "instructorCode" TEXT NOT NULL,
    "title" TEXT,
    "headline" TEXT,
    "specializations" TEXT[],
    "expertise" TEXT[],
    "certifications" TEXT[],
    "yearsOfExperience" INTEGER NOT NULL DEFAULT 0,
    "hourlyRate" DOUBLE PRECISION,
    "rating" DOUBLE PRECISION DEFAULT 0,
    "totalReviews" INTEGER NOT NULL DEFAULT 0,
    "totalStudents" INTEGER NOT NULL DEFAULT 0,
    "totalCourses" INTEGER NOT NULL DEFAULT 0,
    "isVerified" BOOLEAN NOT NULL DEFAULT false,
    "verifiedAt" TIMESTAMP(3),
    "bankAccount" TEXT,
    "bankName" TEXT,
    "paypalEmail" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "instructors_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "user_preferences" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "theme" TEXT NOT NULL DEFAULT 'light',
    "language" TEXT NOT NULL DEFAULT 'en',
    "timezone" TEXT NOT NULL DEFAULT 'UTC',
    "currency" TEXT NOT NULL DEFAULT 'USD',
    "emailNotifications" BOOLEAN NOT NULL DEFAULT true,
    "pushNotifications" BOOLEAN NOT NULL DEFAULT true,
    "smsNotifications" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "user_preferences_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "countries" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "code3" TEXT NOT NULL,
    "phoneCode" TEXT NOT NULL,
    "currency" TEXT NOT NULL,
    "currencySymbol" TEXT NOT NULL,
    "flag" TEXT,
    "emoji" TEXT,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "countries_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "user_profiles_userId_key" ON "user_profiles"("userId");

-- CreateIndex
CREATE INDEX "user_profiles_userId_idx" ON "user_profiles"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "students_userId_key" ON "students"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "students_studentCode_key" ON "students"("studentCode");

-- CreateIndex
CREATE INDEX "students_studentCode_idx" ON "students"("studentCode");

-- CreateIndex
CREATE UNIQUE INDEX "instructors_userId_key" ON "instructors"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "instructors_instructorCode_key" ON "instructors"("instructorCode");

-- CreateIndex
CREATE INDEX "instructors_instructorCode_isVerified_idx" ON "instructors"("instructorCode", "isVerified");

-- CreateIndex
CREATE UNIQUE INDEX "user_preferences_userId_key" ON "user_preferences"("userId");

-- CreateIndex
CREATE INDEX "user_preferences_userId_idx" ON "user_preferences"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "countries_code_key" ON "countries"("code");

-- CreateIndex
CREATE UNIQUE INDEX "countries_code3_key" ON "countries"("code3");

-- CreateIndex
CREATE INDEX "countries_code_idx" ON "countries"("code");
