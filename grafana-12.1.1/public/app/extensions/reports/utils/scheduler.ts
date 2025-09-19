import { dateTime } from '@grafana/data';
import { formatUtcOffset } from '@grafana/ui/internal';

import {
  ReportIntervalFrequency,
  LAST_DAY_OF_MONTH,
  ReportTime,
  SchedulingData,
  ReportSchedulingFrequency,
  SchedulingOptions,
} from '../../types';
import { initialState } from '../state/reducers';

import { createDate, getDate, getTime, padTime } from './dateTime';

/**
 * Process schedule data
 * @param scheduleData
 */
export const getSchedule = (scheduleData = {} as SchedulingData) => {
  const {
    time,
    startDate,
    endDate,
    endTime,
    timeZone,
    frequency,
    dayOfMonth,
    workdaysOnly,
    intervalFrequency,
    intervalAmount,
    sendTime,
  } = scheduleData;

  const parsedTime = !time && startDate ? getTime(String(startDate)) : time;
  const combinedStartDate =
    startDate && sendTime !== 'now' ? createDate(startDate, parsedTime as ReportTime, timeZone) : '';
  const combinedEndDate =
    endDate && ![ReportSchedulingFrequency.Once, ReportSchedulingFrequency.Never].includes(frequency)
      ? createDate(endDate, endTime as unknown as ReportTime, timeZone)
      : '';
  const options = {
    frequency,
    timeZone,
    workdaysOnly,
    intervalFrequency,
    intervalAmount: intervalAmount ? parseInt(intervalAmount, 10) : 0,
    startDate: combinedStartDate,
    endDate: combinedEndDate,
    dayOfMonth: dayOfMonth === LAST_DAY_OF_MONTH ? LAST_DAY_OF_MONTH : '',
  };

  // Remove empty/falsy fields from the schedule object
  return Object.fromEntries(Object.entries(options).filter(([_, val]) => val)) as unknown as SchedulingOptions;
};

export function getOrdinal(n: number) {
  const suffixes = ['th', 'st', 'nd', 'rd'];
  const value = n % 100;
  return n + (suffixes[(value - 20) % 10] || suffixes[value] || suffixes[0]);
}

export const isHourFrequency = (frequency: ReportSchedulingFrequency, interval = ReportIntervalFrequency.Hours) => {
  return frequency === ReportSchedulingFrequency.Custom && interval === ReportIntervalFrequency.Hours;
};

export const showWorkdaysOnly = (frequency: ReportSchedulingFrequency, interval = ReportIntervalFrequency.Hours) => {
  return (
    [ReportSchedulingFrequency.Hourly, ReportSchedulingFrequency.Daily].includes(frequency) ||
    isHourFrequency(frequency, interval)
  );
};

export function parseScheduleTime({
  startDate,
  endDate,
  intervalFrequency = ReportIntervalFrequency.Hours,
  intervalAmount = 2,
  frequency,
  dayOfMonth,
  timeZone,
  workdaysOnly,
}: SchedulingOptions) {
  if (!startDate) {
    return '';
  }

  const locale = 'en-US';
  const { hour: h, minute: m } = getTime(startDate);
  const minute = padTime(m);
  const hour = padTime(h);
  const day = dateTime(getDate(startDate)).locale(locale).format('dddd');
  const date = dayOfMonth === 'last' ? 'last' : getOrdinal((getDate(startDate) as Date).getDate());
  let duration, time;
  const offset = formatUtcOffset(Date.now(), timeZone);
  const timeString = `at ${hour}:${minute}${offset ? ` ${offset}` : ''}`;
  const workdaysOnlyStr = workdaysOnly && showWorkdaysOnly(frequency, intervalFrequency) ? ', Monday to Friday' : '';
  if (endDate) {
    const startStr = dateTime(getDate(startDate)).locale(locale).format('LL');
    const endStr = dateTime(getDate(endDate)).locale(locale).format('LL');
    if (endStr !== startStr) {
      duration = `${startStr} - ${endStr}`;
    } else {
      duration = startStr;
    }
  }

  switch (frequency) {
    case ReportSchedulingFrequency.Monthly:
      time = `Monthly on the ${date} day ${timeString}`;
      break;
    case ReportSchedulingFrequency.Weekly:
      time = `Every ${day} ${timeString}`;
      break;
    case ReportSchedulingFrequency.Daily:
      time = `Daily ${timeString}`;
      break;
    case ReportSchedulingFrequency.Hourly:
      time = `Hourly at minute ${minute}`;
      break;
    case ReportSchedulingFrequency.Custom:
      time = `Every ${intervalAmount} ${intervalFrequency}`;
      break;
    case ReportSchedulingFrequency.Once:
      time = `Once on ${dateTime(getDate(startDate)).locale(locale).format('LL')}`;
      break;
    case ReportSchedulingFrequency.Never:
      time = `Never`;
      break;
    default:
      time = '';
  }

  if (duration && time) {
    return `${time}, ${duration}${workdaysOnlyStr}`;
  } else if (frequency === ReportSchedulingFrequency.Custom) {
    time += `, ${
      intervalFrequency === ReportIntervalFrequency.Hours
        ? `from ${hour}:${minute}${offset ? ` ${offset}` : ''}`
        : `from ${dateTime(getDate(startDate)).locale(locale).format('LL')}`
    }`;
  }

  return time + workdaysOnlyStr;
}

const recurrenceMap = new Map([
  [ReportSchedulingFrequency.Monthly, 'month'],
  [ReportSchedulingFrequency.Daily, 'day'],
  [ReportSchedulingFrequency.Weekly, 'week'],
  [ReportSchedulingFrequency.Hourly, 'hour'],
]);

export const schedulePreview = (schedule: SchedulingData) => {
  const { frequency, intervalFrequency = ReportIntervalFrequency.Hours, intervalAmount = '2' } = schedule;
  if (frequency === ReportSchedulingFrequency.Never) {
    return 'This report will not be sent.';
  }
  const workdaysOnlySuffix = schedule.workdaysOnly ? ', Monday to Friday.' : '.';
  const preview: string[] = [];

  if (!schedule.startDate) {
    preview.push("This report will be sent immediately after it's saved");
    const recurrence =
      frequency === ReportSchedulingFrequency.Custom
        ? `${intervalAmount} ${intervalFrequency}`
        : recurrenceMap.get(frequency);

    if (recurrence) {
      preview.push(`and then every ${recurrence}`);
    }

    return preview.join(' ') + workdaysOnlySuffix;
  }

  const scheduleTime = parseScheduleTime(getSchedule(schedule));

  if (scheduleTime) {
    preview.push(`This report will be sent: ${scheduleTime}.`);
  }

  return preview.join(' ');
};

export const scheduleUpdated = (newSchedule: Partial<SchedulingOptions>) => {
  const originalSchedule = initialState.report.schedule;

  if (Object.keys(originalSchedule).length !== Object.keys(newSchedule).length) {
    return true;
  }

  return Object.entries(originalSchedule).some(([key, value]) => value !== newSchedule[key as keyof SchedulingOptions]);
};
