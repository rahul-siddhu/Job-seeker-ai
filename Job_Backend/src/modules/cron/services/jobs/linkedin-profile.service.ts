import mongoose from 'mongoose'
import axios from 'axios'
import { getLinkPreview } from 'link-preview-js'

/**
 * Fetch LinkedIn profile data for a job and store it in the database.
 * @param {string} designation - Designation for the profiles.
 * @param {string} company - Company name for the profiles.
 * @param {string} jobId - MongoDB ObjectId of the job.
 * @returns {Promise<void>}
 */
export async function fetchLinkedInProfilesForJob(
  designation: string,
  company: string,
  jobId: string
): Promise<void> {
  try {
    const jobObjectId = new mongoose.Types.ObjectId(jobId)

    // Fetch LinkedIn profiles from the external service
    const response = await axios.post('http://43.204.161.69:8989/get_profiles', { designation, company })
    console.log("designation", designation)
    console.log("company", company)
    
    const { top_profiles } = response.data

    // If no profiles are found, create an empty document
    if (!top_profiles || top_profiles.length === 0) {
      Logger.warn(`No profiles found for designation: ${designation} and company: ${company}. Creating empty document.`)

      // Create a blank LinkedIn profile document
      await App.Models.LinkedInProfile.create({
        _job: jobObjectId,
        linkedInProfileData: [],
      })
      Logger.info('Blank LinkedIn profile document created for job:', jobObjectId)
      return
    }

    // Process valid profiles
    const profileDataPromises = top_profiles.map(async (profileUrl: string) => {
      try {
        console.log(profileUrl)
        const previewData = await getLinkPreview(profileUrl)

        const name = 'title' in previewData ? previewData.title : 'Unknown'
        const images = 'images' in previewData ? previewData.images : []
        const profilePicUrl = images.length > 0 ? images[0] : ''

        return {
          name,
          profilePic: {
            name: 'Profile Picture',
            key: 'profile_pic',
            url: profilePicUrl,
          },
          profileUrl,
        }
      } catch (error) {
        console.error(`Error fetching metadata for ${profileUrl}:`, error)
        return null
      }
    })

    // Wait for all profile data to be processed
    const profilesData = await Promise.all(profileDataPromises)

    // Filter out any invalid profiles
    const validProfiles = profilesData.filter((profile) => profile !== null)

    // If no valid profiles were found, create a blank document
    if (validProfiles.length === 0) {
      Logger.warn('No valid LinkedIn profiles could be processed. Creating empty document.')

      await App.Models.LinkedInProfile.create({
        _job: jobObjectId,
        linkedInProfileData: [],
      })
      Logger.info('Blank LinkedIn profile document created for job:', jobObjectId)
      return
    }

    // Save the valid profiles to the database
    await App.Models.LinkedInProfile.create({
      _job: jobObjectId,
      linkedInProfileData: validProfiles,
    })

    Logger.info('LinkedIn profiles saved successfully for job:', jobObjectId)
  } catch (error) {
    Logger.error('Error fetching LinkedIn profiles for job:', error)
    throw error
  }
}
