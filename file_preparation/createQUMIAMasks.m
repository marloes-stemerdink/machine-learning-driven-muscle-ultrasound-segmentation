%% Script to convert QUMIA masks to PNG files for segmentation script.
% Authors: Jeroen van Doorn, Marloes Stemerdink
% Last update: 15-06-2026
clc;
clear;

%% Format and changes
% Input: 
% - folder with subfolders for each participant. Subfolder name should be
% participant code
% - subfolders include ultrasound images with specified ROIs. Meaning there
% are .tif files and a subfolder called 'roi', with a file called anal.mat
% - file with all muscle codes (Muscles.xlsx)

% Output
% - folder called 'group'_new, with subfolders 'images' and 'masks'.
% - 'images' contains .dcm files of all images, with a new filename
% - 'masks' contains .png files of all masks. Filename matches the image
% - note: participants are no longer in seperate subfolders 
% filename breakdown: participantID_musclecode_sidecode_measurementnumber
% muscle codes can be found in Muscles.xlsx
% sidecode: Left=00, Right=01

%% Script
group = 'klinisch_compleet';

% Define input and output folders, create if output is non-existent
base_input = fullfile(pwd,group);
base_output = fullfile(pwd,append(group,'_new'));

destinationfolder_images = fullfile(base_output, 'images');
destinationfolder_masks = fullfile(base_output, 'masks');
if ~exist(destinationfolder_images, 'dir'), mkdir(destinationfolder_images); end
if ~exist(destinationfolder_masks,  'dir'), mkdir(destinationfolder_masks);  end

% variable with muscle codes
lookup = readtable('Muscles.xlsx');

% define participant folders
participant_folders = dir(fullfile(pwd, group, '*'));
participant_folders = participant_folders([participant_folders.isdir] & ~ismember({participant_folders.name},{'.','..'}));

missing_muscles = {};

% Loop through all participant subfolders
for p = 1:numel(participant_folders)
    muscle_count = containers.Map('KeyType','char','ValueType','double');   % counter per muscle
    participant = participant_folders(p).name;
    participant_path = fullfile(pwd, group, participant);

    num_str = regexp(participant, '\d+$', 'match', 'once');  % extract trailing digits e.g. '002', '1005'
    participant_id = sprintf('%05d', str2double(num_str));           % zero-pad to 5 digits

    % create participant subfolders in destination
    % out_images = fullfile(destinationfolder_images,participant);
    % out_masks = fullfile(destinationfolder_masks, participant);
    % if ~exist(out_images, 'dir'), mkdir(out_images); end
    % if ~exist(out_masks, 'dir'), mkdir(out_masks); end

    % load segmentation information from participant's roi folder
    load(fullfile(participant_path, 'roi', 'anal.mat'))

    for i = 1:size(dcmfiles, 2)
    
        if ~isempty(rois{i})
        
            % load image including metadata
            im = dicomread(fullfile(participant_path, dcmfiles{i}));
            info = dicominfo(fullfile(participant_path,dcmfiles{i}));
            
            % get imaging field for conveniency
            minY = info.SequenceOfUltrasoundRegions.Item_1.RegionLocationMinY0;
            maxY = info.SequenceOfUltrasoundRegions.Item_1.RegionLocationMaxY1;
            minX = info.SequenceOfUltrasoundRegions.Item_1.RegionLocationMinX0;
            maxX = info.SequenceOfUltrasoundRegions.Item_1.RegionLocationMaxX1;
            
            % find the actual imaging field an calculate the margin
            crop = im2gray(im(minY+50:maxY-50, minX+50:maxX-50, :));
            xl = find(mean(crop) > 5, 1, 'first') + minX + 50 - 1;
            xr = find(mean(crop) > 5, 1, 'last') + minX + 50 - 1;
            margin = round(0.15 * numel(xl:xr));
            
            % convert roi vertices to mask
            mask = uint8(poly2mask(rois{i}(1,:), rois{i}(2, :), size(im, 1), size(im, 2)));
            
            % code exclusion fields
            mask([1:minY maxY:size(im, 1)], :) = 255;
            mask(:, [1:xl xr:size(im, 2)]) = 255;
            mask(:, [xl:xl+margin xr-margin:xr]) = 255;
  
            mask_vis = mask;
            mask_vis(mask_vis == 255) = 2;   % remap ignore to class 2

            % % plot image and mask
            % figure(1)
            % ax1 = subplot(1, 2, 1);
            % imagesc(im)
            % axis image
            % 
            % ax2 = subplot(1, 2, 2);
            % imagesc(mask_vis)
            % axis image
            % 
            % clim([0 2])
            % colormap(ax2, [0 0 0; ...
            %     0 1 0; ...
            %     1 0 0])
            % linkaxes([ax1 ax2], 'xy')  % x and y axes are linked

            % % plot
            % figure(1)
            % ax1 = subplot(1, 2, 1);
            % imagesc(im)
            % axis image
            % 
            % ax2 = subplot(1, 2, 2);
            % imagesc(mask_vis)
            % axis image
            % 
            % clim([0 2])
            % colormap(ax2, [0 0 0; ...
            %     0 1 0; ...
            %     1 0 0])
            % linkaxes([ax1 ax2], 'xy')  % x and y axes are linked
            
            % lookup muscle code
            muscle = muscles{i};
            idx_lookup = find(strcmpi(strtrim(lookup.Muscle),strtrim(muscle)), 1);

            if isempty(idx_lookup)
                missing_muscles{end+1} = sprintf( ...
                    "Muscle '%s' is not in lookup.Muscle, skipping file: %s", ...
                    muscle, info.Filename);
            
                continue;
            end
            code = lookup.Code{idx_lookup};

            % Determine side code
            if sides{i} == 'L'
                sidecode = '00';
            elseif sides{i} == 'R'
                sidecode = '01';
            else
                disp("Side unknown: ", sides{i})
            end
            
            % Count images per muscle+side combination
            muscle_side_key = strcat(muscle, '_', sides{i});

            if isKey(muscle_count, muscle_side_key)
                muscle_count(muscle_side_key) = muscle_count(muscle_side_key)+1;
            else
                muscle_count(muscle_side_key)=1;
            end

            idx = muscle_count(muscle_side_key);

            % save image and mask into participant subfolders
            filename = sprintf('%s_%s_%s_%02d',participant_id,code,sidecode,idx);
            fprintf("Saving: %s\n", filename);

            copyfile(fullfile(participant_path, dcmfiles{i}), fullfile(destinationfolder_images, [filename '.dcm']));
            imwrite(mask, fullfile(destinationfolder_masks, [filename '.png']));

        end
    end
end

% Print which muscles were missing in the muscle code file. Those files
% were not copied and converted
fprintf('\n=== Missing muscles ===\n')
disp(string(missing_muscles'))