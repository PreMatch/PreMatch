require 'google/cloud/datastore'

class Database
  def initialize
    @datastore = Google::Cloud::Datastore.new project: PROJECT_ID
  end

  private

  PROJECT_ID = 'prematch-212912'
end