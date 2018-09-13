require 'google/cloud/datastore'

class Database
  def initialize
    @datastore = Google::Cloud::Datastore.new project: PROJECT_ID
  end

  def read_schedule(handle)
    key = @datastore.key 'Schedule', handle
    @datastore.find key
  end

  def register_association(user_id, handle)
    task = @datastore.entity 'Discord', user_id do |t|
      t['handle'] = handle
    end
    @datastore.save task
  end

  def associated_handle(user_id)
    key = @datastore.key 'Discord', user_id.to_s
    entity = @datastore.find(key)

    if entity.nil?
      nil
    else
      entity['handle']
    end
  end

  private

  PROJECT_ID = 'prematch-212912'.freeze
end