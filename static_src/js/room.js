import $ from 'jquery';
import autosize from 'autosize';
import ResizeObserver from 'resize-observer-polyfill';


/*
** JavaScript for Conversate
*/

$('document').ready(function () {

  /**************************************************************************
  *********************************************************** Global vars
  **************************************************************************/

  // Settings
  var settings = $.extend({
    // API urls
    apiCheck: null,
    apiSend: null,
    apiHistory: null,

    // PK of last message
    last: 0,

    // If True, will alert when changes occur while window blurred
    alertEnabled: false,

    // Server time, for initial time updates
    serverTime: time(),

    // Settings taken from converse.settings
    idleAt: 60 * 1000,
    pollMin: 5 * 1000,
    pollMax: 60 * 1000,
    pollStep: 5 * 1000
  }, window.CONVERSATE || {});

  // Internal constants
  var // jQuery animation interval limits
    FX_INTERVAL_MIN = 250,
    FX_INTERVAL_MAX = 1000,

    // Minimum scrollbar height, so it's still visible on long convs
    MIN_SCROLLBAR_HEIGHT = 10,

    // Maximum number of lines to update the time on
    // Avoids crashing the browser when there is a long archive
    UPDATE_TIME_MAXLINES = 50
    ;

  // Detect DOM elements
  var $window = $(window),
    $body = $('body'),
    $conv = $('.cnv_messages'),
    $content = $conv.parent(),
    $input = $('.cnv_input'),
    $input_form = $input.find('form'),
    $message = $input_form.find('textarea[name="content"]'),
    $file = $input_form.find('input[name="file"]'),
    $fileToggle = $input_form.find('#cnv_input__toggler-file'),
    $users = $('.cnv_users'),
    $convTable = $conv.find('tr').parent(),
    $convTableCon = $('.cnv_table_con')
    ;

  // Prep content regex
  var urlPattern = new RegExp(
    '\\b('
    + 'https?://' // http:// or https://
    + '(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\\.)+(?:[A-Z]{2,6}\\.?|[A-Z0-9-]{2,}\\.?)|' // domain...
    + '[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?|' // ...or network name
    + '\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}|'  // ...or ipv4
    + '\\[?[A-F0-9]*:[A-F0-9:]+\\]?)'  // ...or ipv6
    + '(?::\\d+)?'  // optional port
    // everything in up to but excluding the trailing /
    + '(?:[/?]\\S*[^\\s`!()\\[\\]{};:\'".,<>?]|/)?' // URL which doesn't end in punctuation
    + ')',

    'gi'
  );
  var imgPattern = new RegExp('\\[\\[\\s*(?:img|image):([^\\]]+)\\s*\\]\\]')


  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;")
      ;
  }

  /**************************************************************************
  *********************************************************** Classes
  **************************************************************************/


  /** Poll manager
  */
  function PollManager(room) {
    this.room = room;
  }
  PollManager.prototype = $.extend(PollManager.prototype, {
    interval: settings.pollMin,
    active: false,
    timeout: null,

    start: function () {
      /** Start the timer for the next poll */
      var thisPoll = this;

      // Clear old timer
      if (this.timeout) {
        clearTimeout(this.timeout);
      }

      // Now polling
      this.active = true;
      this.timeout = setTimeout(
        function () {
          thisPoll.timeout = null;
          thisPoll.poll();
        },
        this.interval
      );
      this.room.status.wait(this.interval);

      // Increase the polling interval
      if (this.interval < settings.pollMax) {
        this.interval += settings.pollStep;
      }
    },
    stop: function () {
      /** Stop polling
          Used when making a request
      */
      this.active = false;
      if (this.timeout) {
        clearTimeout(this.timeout);
        this.timeout = null;
      }
      this.room.status.stop();
    },
    poll: function () {
      this.stop();
      this.room.status.loading();
      this.room.check();
    },
    activity: function () {
      /** Call when activity has occurred
          Resets the interval to the minimum
      */
      this.interval = settings.pollMin;
    }
  });


  /** Status manager
      Track idle state and window focus
      Manage action and poll indicators
  */
  function Status(room) {
    var thisStatus = this;
    this.room = room;
    this.idleSince = 0;
    this.unseenActivity = false;
    this.hasFocus = true;

    // Monitor idleness
    this.resetIdle();
    $body
      .mousemove(function () { thisStatus.resetIdle(); })
      .keypress(function () { thisStatus.resetIdle(); })
      ;

    // Monitor window focus state
    $window
      .focus(function () {
        thisStatus.hasFocus = true;
        thisStatus._restore();
      })
      .blur(function () {
        thisStatus.hasFocus = false;
      })
      ;

    if (settings.alertEnabled) {
      // Set up interval to watch for idleness (10 seconds)
      // If message arrives while idle, will alert immediately
      // However, we also need to watch in case if message arrives
      // before the idle timer runs out
      setInterval(function () {
        if (thisStatus.unseenActivity && thisStatus.isIdle()) {
          // Idle and messages to see. Alert.
          thisStatus.alert();
        }
      }, 10 * 1000);
    }
  }
  Status.prototype = $.extend(Status.prototype, {
    // Title flasher
    flasher: null,
    $timer: null,
    $note: null,

    render: function ($el) {
      /** Render status display elements */
      // Add timer elements
      var $con = $('<div class="cnv_hourglass_con"></div>')
        .appendTo($el)
        ;
      this.$hourglass = $('<div class="cnv_hourglass"></div>')
        .appendTo($con)
        ;
      this.$note = $('<div class="cnv_hourglass_note"></div>')
        .appendTo($con)
        ;

      // Handle double clicks on hourglass
      var thisStatus = this,
        DOUBLE_CLICK_TOLERANCE = 500,
        lastClick = 0
        ;
      $con.click(function (e) {
        e.preventDefault();

        var now = (new Date()).getTime();
        if (now - lastClick > DOUBLE_CLICK_TOLERANCE) {
          lastClick = now;
          return;
        }

        thisStatus.$note.text('Reloading...');
        if (thisStatus.room.poll.active) {
          // Reset poll interval, then jump to the next poll
          thisStatus.room.poll.activity();
          thisStatus.room.poll.poll();
        } else {
          // Assume something has failed - reload the page
          window.location.reload();
        }
      });
    },

    resetIdle: function () {
      this.idleSince = (new Date()).getTime();
      this.unseenActivity = false;
    },
    isIdle: function () {
      var now = (new Date()).getTime();
      return (now - this.idleSince > settings.idleAt);
    },
    activity: function () {
      // If focus, cannot alert
      if (this.hasFocus) {
        return;
      }

      // Start flashing if is idle
      if (this.isIdle()) {
        this.alert();
      } else {
        // Otherwise tell idle handler that there are messages pending
        this.unseenActivity = true;
      }
    },
    loading: function () {
      this.$note.text('Loading...');
    },
    sending: function () {
      this.$note.text('Sending...');
    },
    stop: function () {
      this.$hourglass.stop(true).animate({ width: 0 }, 0);
    },
    wait: function (time) {
      // Clear the timer note
      this.$note.text('');

      // Calculate jQuery animation speed
      var fx_interval = (
        FX_INTERVAL_MAX - FX_INTERVAL_MIN
      ) * (
          this.room.poll.interval / settings.pollMax
        );
      fx_interval += FX_INTERVAL_MIN;
      $.fx.interval = parseInt(fx_interval, 10);

      // Show the timer
      this.$hourglass
        .animate({ width: 0 }, 0)
        .animate({ width: '100%' }, this.room.poll.interval, 'linear')
        ;

    },
    alert: function () {
      // Alert the user that something has happened
      if (!settings.alertEnabled) {
        return;
      }

      // If there's already a flasher, let that do its thing
      if (this.flasher) {
        return;
      }
      this._flash();

      // Send notification
      new Notification('Chat activity')
    },

    _flash: function () {
      var thisStatus = this,
        interval = 500
        ;

      // If we've regained focus (or had it already), and we're not idle,
      // make sure the title is reset, then end flasher
      if (this.hasFocus && !this.isIdle()) {
        this._restore();
        return;
      }

      // Flash the title
      document.title = '**********';
      $conv.css('background-color', '#ccc');

      // Set up the timer to restore and continue the flashing
      this.flasher = setTimeout(function () {
        thisStatus._restore();

        // If we don't have focus or are still idle, we'll need to flash it
        if (!this.hasFocus || this.isIdle()) {
          thisStatus.flasher = setTimeout(function () {
            thisStatus._flash();
          }, interval);
        }

      }, interval);
    },
    _restore: function () {
      // Restore the title
      document.title = 'Talk';
      $conv.css('background-color', '#fff');

      // If we're flashing, clear the flasher
      if (this.flasher) {
        clearTimeout(this.flasher);
        this.flasher = undefined;
      }
    }
  });


  /** Room
      Manages messages
      Controls helper classes
  */
  function Room() {
    var thisRoom = this;

    // Instantiate helpers
    this.status = new Status(this);
    this.poll = new PollManager(this);
    this.input = new Input(this);

    // Detect the CSRF middleware token
    this.csrfToken = $input_form.find('input[name="csrfmiddlewaretoken"]').val();

    // Pull list of users
    var $userThs = $users.find('th');
    this.users = {};
    for (var i = 0; i < $userThs.length; i++) {
      this.users[$($userThs[i]).text()] = $($userThs[i]);
    }

    // Find and categorise time cells, and set up intervals
    this.timeCells = { 0: [], 1: [], 2: [], 3: [], 4: [] };
    var $cell, cellTime, interval, now = time();
    $convTable.find('td:first-child').each(function () {
      $cell = $(this);
      cellTime = parseInt($cell.attr('data-time'), 10);
      // If time is in the past, check once a minute
      thisRoom.timeCells[unitTimeRelative(cellTime, now) || 2].push(
        [$cell, cellTime]
      );
    });

    setInterval(function () { thisRoom.updateTimes(1); }, 0.5 * 1000);
    setInterval(function () { thisRoom.updateTimes(2); }, 30 * 1000);
    setInterval(function () { thisRoom.updateTimes(3); }, 60 * 30 * 1000);
    setInterval(function () { thisRoom.updateTimes(4); }, 60 * 60 * 12 * 1000);

    // Render content
    $convTable.find('td:last-child').each(function () {
      $cell = $(this);
      $cell.html(thisRoom._render($cell.html()));
    });

    // Replace first line with controller
    if (settings.remaining) {
      this.$history = $('<a href="javascript:void(0);" />')
        .click(function (e) {
          e.preventDefault();
          thisRoom.fetchHistory();
        })
        ;
      this.$firstRow = $convTable.find('tr:first-child');
      this.$firstRow.find('td:last-child')
        .html(this.$history)
        ;
      this._fetchHistory({
        first: settings.first,
        remaining: settings.remaining,
        messages: []
      });
    }

    // Scroll down to bottom
    this._scrollToBottom();

    // Listen for resize
    const observer = new ResizeObserver((entries, observer) => {
      for (const entry of entries) {
        this._scrollToBottom();
      }
    });
    observer.observe($conv.get(0));

    $convTable.click(e => {
      $message.focus();
    });

    // Request browser notification permission
    Notification.requestPermission();

    // Set everything going
    this.poll.start();
  }
  Room.prototype = $.extend(Room.prototype, {
    // PK of last message
    last: settings.last,

    // Difference in time between server and client
    timeDiff: 0,

    // Track time cells
    // { interval: [  [$cell, time], [$cell, time] ... ] ... }
    timeCells: null,

    // Request queue
    _requesting: false,
    _requestQueue: [],

    fetchHistory: function () {
      var thisRoom = this;
      $.ajax({
        cache: false,
        type: 'POST',
        url: settings.apiHistory,
        data: {
          'first': this.first,
          'csrfmiddlewaretoken': this.csrfToken
        },
        dataType: 'json',
        success: function (data) {
          thisRoom._fetchHistory(data);
        },
        error: function (jqXHR, textStatus, errorThrown) {
          thisRoom.poll.start();
          thisRoom.error(errorThrown);
        }
      });
    },
    _fetchHistory: function (data) {
      this.first = data.first;
      this.remaining = data.remaining;

      var i, m, $newLine;
      for (i = 0; i < data.messages.length; i++) {
        m = data.messages[i];
        $newLine = this._mkLine(m.msgTime, m.user, m.content)
          .insertAfter(this.$firstRow)
          ;
        this.timeCells[unitTimeRelative(m.msgTime)].push(
          [$newLine.find('.cnv_time'), m.msgTime]
        );
      }

      if (this.remaining === 0) {
        this.$history.parent().text('No older messages');
      } else {
        this.$history.text(
          this.remaining + ' older message' + (
            this.remaining == 1 ? '' : 's'
          )
        );
      }
    },

    check: function () {
      this._request(settings.apiCheck, new FormData());
    },
    send: function (formData) {
      this._request(settings.apiSend, formData);
    },
    error: function (msg) {
      this._add(time(), 'ERROR', msg + '<br><a href=".">Reload</a>');
    },
    _request: function (url, data) {
      // Queue requests
      if (this._requesting) {
        this._requestQueue.push([url, data]);
        return;
      }
      this._requesting = true;

      // Make request
      var thisRoom = this;
      data.append('last', this.last || 0);
      data.append('csrfmiddlewaretoken', this.csrfToken);
      data.append('hasFocus', this.status.hasFocus);
      $.ajax({
        cache: false,
        type: 'POST',
        url: url,
        data: data,
        dataType: 'json',
        processData: false,
        contentType: false,
        success: function (data) {
          thisRoom._response(data);
        },
        error: function (jqXHR, textStatus, errorThrown) {
          thisRoom.poll.start();
          thisRoom.error(errorThrown);
        }
      });
    },
    _response: function (data) {
      // Catch error
      if (!data.success) {
        this.error(data.error);
        this.poll.start();
        return;
      }

      // Store data
      this.last = data.last;
      this.setTimeDiff(data.time);

      // Add messages
      for (var i = 0, l = data.messages.length; i < l; i++) {
        var message = data.messages[i];
        this._add(message.time, message.user, message.content);
      }

      // Check for activity
      if (data.messages.length > 0) {
        this.poll.activity();
      }

      // Update user data
      this._updateUsers(data.users);

      // See if there's anything on the request queue
      this._requesting = false;
      if (this._requestQueue.length > 0) {
        this._request.apply(this, this._requestQueue.shift());
        return;
      }

      // Start new poll
      this.poll.start();
    },
    _mkLine: function (msgTime, user, content) {
      // Add new line and register time cell
      return $(
        '<tr class="cnv_user_' + user + '">'
        + '<td class="cnv_time" data-time="' + msgTime + '"></td>'
        + '<td class="cnv_user">' + user + '</td>'
        + '<td class="cnv_content">' + this._render(content) + '</td>'
        + '</tr>'
      );
    },
    _add: function (msgTime, user, content) {
      var $newLine = this._mkLine(msgTime, user, content)
        .appendTo($convTable)
        ;
      this.timeCells[unitTimeRelative(msgTime)].push(
        [$newLine.find('.cnv_time'), msgTime]
      );

      // Scroll down to bottom
      this._scrollToBottom();

      // Tell the status manager that activity has occurred
      this.status.activity();
    },
    _scrollToBottom: function () {
      const el = $conv.get(0);
      el.scrollTop = el.scrollHeight;
    },
    _render: function (content) {
      /** Render content */
      return content;
    },
    _updateUsers: function (users) {
      var $el, name, found = {}, del = $.extend({}, this.users);
      for (var i = 0, l = users.length; i < l; i++) {
        // Find the user
        name = users[i].username;
        $el = this.users[name];
        if ($el) {
          // Found
          found[name] = $el;
          delete (del[name]);
        } else {
          // Does not exist yet
          // They don't exist, add in position
          var $row = $('<tr/>');
          $el = $('<th>' + name + '</th>').appendTo($row);
          $row
            .append($('<td/>'))
            .appendTo($users)
            ;
          found[name] = $el;
        }

        // Update and pop from del
        $el.parent().attr(
          'class',
          'cnv_user_' + name + ' '
          + (
            users[i].active ? (
              users[i].has_focus ? 'cnv_active' : 'cnv_afk'
            ) : 'cnv_inactive'
          )
        );
        $el.next()
          .text(humanTime(users[i].last_spoke))
          .attr('title', 'Last ping: ' + humanTime(users[i].last_seen))
          ;
      }

      // Delete any deleted
      for (i = 0; i < del.length; i++) {
        del[i].remove();
      }
      this.users = found;
    },

    setTimeDiff: function (serverTime) {
      this.timeDiff = time() - serverTime;
    },
    updateTimes: function (unit) {
      // Don't need to update the seconds if they're idle
      if (unit < 2 && this.status.isIdle()) {
        return;
      }
      var cells = this.timeCells[unit],
        newCells = [],
        length = cells.length,
        start = 0,
        now = time() - this.timeDiff,
        i, cell, timeDelta, newUnit
        ;

      for (i = 0; i < length; i++) {
        // Update text
        cell = cells[i];
        timeDelta = now - cell[1];
        newUnit = unitTime(timeDelta);
        cell[0].text(humanTime(timeDelta, newUnit));

        // If the unit has changed, move to different timeCell group
        if (unit < 4 && unit != newUnit) {
          this.timeCells[unit + 1].push(cell);
        } else {
          newCells.push(cell);
        }
      }
      this.timeCells[unit] = newCells;
    }
  });


  /** Input handler
  */
  function Input(room) {
    var thisInput = this;
    this.room = room;

    // Remove the username and move the input button
    var $inputTable = $input.find('table'),
      $col1 = $($inputTable.find('td').get(0)),
      $col2 = $($inputTable.find('td').get(1))
      ;
    $col2.html($col1.html());
    $col1.empty();

    // Make the input button autogrow
    autosize($message);

    // Override enter keypress
    $message.keyup(
      event => {
        // Enter without shift, submit
        if (event.keyCode == 13 && !event.shiftKey) {
          $input_form.submit();
        }
      }
    ).keydown(
      event => {
        // Suppress enter without shift to avoid growing the field
        if (event.keyCode == 13 && !event.shiftKey) {
          event.preventDefault();
        }
      }
    );

    // Override form submit
    $input_form.submit(function () {
      return thisInput.submit();
    });

    // Tell the status indicator it can set up
    this.room.status.render($col1);
  }
  Input.prototype = $.extend(Input.prototype, {
    submit: function () {
      // Check there's data
      if (!$message.val()) {
        // ++ TODO: feedback
        return false;
      }

      // Get message from form
      var formData = new FormData($input_form[0]);

      // Reset form
      $message.val('');
      $file.val('');
      $fileToggle.prop('checked', false);
      autosize.update($message);
      $message.focus();

      // Send message
      this.room.poll.stop();
      this.room.status.sending();
      this.room.send(formData);

      // Forbid normal submission
      return false;
    }
  });


  /**************************************************************************
  *********************************************************** Functions
  **************************************************************************/

  function time() {
    return Math.round(new Date().getTime() / 1000);
  }

  function unitTimeRelative(from, to) {
    if (!to) {
      to = time();
    }
    return unitTime(to - from);
  }

  function unitTime(delta) {
    /** Return an integer representing the time delta
        0   Less than 0
        1   Seconds
        2   Minutes
        3   Hours
        4   Days
    */
    if (delta < 0) {
      return 0;
    } else if (delta < 60) {
      return 1;
    } else if (delta < 60 * 60) {
      return 2;
    } else if (delta < 60 * 60 * 24) {
      return 3;
    } else {
      return 4;
    }
  }

  var TIME_UNITS = ['never', 'second', 'minute', 'hour', 'day'],
    TIME_DENOM = [1, 1, 60, 60 * 60, 60 * 60 * 24]
    ;
  function humanTime(delta, unit) {
    var term, val;
    if (delta < 0) {
      return TIME_UNITS[0];
    }
    if (!unit) {
      unit = unitTime(delta);
    }

    val = Math.floor(delta / TIME_DENOM[unit]);
    return '' + val + ' ' + TIME_UNITS[unit] + (val == 1 ? '' : 's');
  }


  /**************************************************************************
  *********************************************************** Activate
  **************************************************************************/

  // Check for elements
  function testEl(name, $el) {
    if (!$el.length) {
      var err = alert;
      if (window.console) {
        err = console.log;
      }
      err('Could not find required element for ' + name);
      return false;
    }
    return true;
  }
  if (
    !testEl('input container', $input) ||
    !testEl('input form', $input_form) ||
    !testEl('input field', $message) ||
    !testEl('content container', $content) ||
    !testEl('message container', $conv) ||
    !testEl('message table', $convTable)
  ) {
    // Required element not found - abort
    return;
  }

  // Create the room, activating polling etc
  room = new Room();
  room.setTimeDiff(settings.serverTime);
});

