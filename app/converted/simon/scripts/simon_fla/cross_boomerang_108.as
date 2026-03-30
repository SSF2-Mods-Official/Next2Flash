package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class cross_boomerang_108 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var decelPercent:*;
        public var offscreenTimer:FrameTimer;
        public var stalled:*;
        public var flipdir:*;
        public var character:*;
        public var maxSpeed:*;
        public var turnThreshold:*;

        public function cross_boomerang_108()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 18, this.frame19, 19, this.frame20, 20, this.frame21, 21, this.frame22, 22, this.frame23, 23, this.frame24);
        }

        public function slowIt():void
        {
            var _local_1:* = (this.self.getXSpeed() * this.decelPercent);
            this.self.setXSpeed(_local_1);
            if (Math.abs(_local_1) <= this.turnThreshold)
            {
                this.self.destroyTimer(this.slowIt);
                this.stalled = true;
                this.self.updateAttackBoxStats(1, {"direction":110});
                this.self.refreshAttackID();
                this.self.addEventListener(SSF2Event.PROJ_COLLIDE, this.catchIt);
                this.self.createTimer(1, -1, this.stallIt);
                this.self.createTimer(5, 1, this.startWallCheck);
            };
        }

        public function stallIt():void
        {
            var _local_1:* = this.self.getXSpeed();
            if (!this.self.isFacingRight())
            {
                _local_1 *= -1;
            };
            if (this.flipdir)
            {
                if (_local_1 < this.maxSpeed)
                {
                    _local_1++;
                    if (_local_1 > this.maxSpeed)
                    {
                        _local_1 = this.maxSpeed;
                    };
                    this.self.setXSpeed(_local_1, false);
                };
            }
            else if (_local_1 > -(this.maxSpeed))
            {
                _local_1--;
                if (_local_1 < -(this.maxSpeed))
                {
                    _local_1 = -(this.maxSpeed);
                };
                this.self.setXSpeed(_local_1, false);
            };
            var _local_2:MovieClip = SSF2API.getCamera().getMC();
            var _local_3:MovieClip = SSF2API.getStage().getMidground();
            var _local_4:* = this.self.getX();
            var _local_5:* = this.self.getY();
            if ((_local_4 < ((_local_2.x - (_local_2.width / 2)) - _local_3.x)) || (_local_4 > ((_local_2.x + (_local_2.width / 2)) - _local_3.x)) || (_local_5 < ((_local_2.y - (_local_2.height / 2)) - _local_3.y)) || (_local_5 > ((_local_2.y + (_local_2.height / 2)) - _local_3.y)))
            {
                this.offscreenTimer.tick();
                if (this.offscreenTimer.completed)
                {
                    this.self.destroy();
                };
            }
            else
            {
                this.offscreenTimer.reset();
            };
        }

        public function flipIt(_arg_1:*=null):*
        {
            if (!this.stalled)
            {
                this.self.destroyTimer(this.slowIt);
                this.stalled = true;
                this.flipdir = true;
                this.self.addEventListener(SSF2Event.HIT_WALL, this.self.destroy);
                this.self.createTimer(1, -1, this.stallIt);
            };
        }

        public function catchIt(_arg_1:*=null):*
        {
            var _local_2:* = undefined;
            if ((_arg_1.data.caller == this.self) && (_arg_1.data.opponent == this.character) && !(this.self.isReversed()))
            {
                if (this.character.getCharacterStat("statsName") == "simon")
                {
                    _local_2 = this.character.getMC().xframe;
                    if ((_local_2 == "stand") || (_local_2 == "walk") || (_local_2 == "run") || (_local_2 == "jump") || (_local_2 == "jump_midair") || (_local_2 == "fall") || (_local_2 == "skid") || (_local_2 == "taunt") || (_local_2 == "crouch"))
                    {
                        if (this.character.isOnGround())
                        {
                            this.character.forceAttack("b_forward", "catch");
                        }
                        else
                        {
                            this.character.forceAttack("b_forward_air", "catch");
                        };
                    };
                };
                this.self.destroy();
            };
        }

        public function startWallCheck():void
        {
            this.self.addEventListener(SSF2Event.HIT_WALL, this.self.destroy);
        }

        public function afterImage():void
        {
            var _local_1:* = undefined;
            if (!this.self.inState(PState.DEAD))
            {
                _local_1 = this.self.applyPalette(this.self.attachEffect("CrossAfterimage", {"behind":true}));
            };
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.decelPercent = 0.9;
            this.offscreenTimer = new FrameTimer(60);
            this.stalled = false;
            this.flipdir = false;
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                this.maxSpeed = this.self.getProjectileStat("xspeed");
                this.turnThreshold = (this.maxSpeed * 0.1);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD, this.flipIt);
                this.self.addEventListener(SSF2Event.REVERSE, this.flipIt);
                this.self.createTimer(4, 0, this.afterImage);
            };
        }

        internal function frame2():*
        {
            this.self.createTimer(1, -1, this.slowIt);
        }

        internal function frame19():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame20():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.destroyTimer(this.slowIt);
            this.self.destroyTimer(this.stallIt);
            this.self.destroyTimer(this.afterImage);
        }

        internal function frame21():*
        {
            this.self.stancePlayFrame("suspend");
        }

        internal function frame22():*
        {
            this.self = SSF2API.getProjectile(this);
            this.decelPercent = 0.9;
            this.offscreenTimer = new FrameTimer(60);
            this.stalled = false;
            this.flipdir = false;
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                this.maxSpeed = this.self.getProjectileStat("xspeed");
                this.turnThreshold = (this.maxSpeed * 0.1);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD, this.flipIt);
                this.self.addEventListener(SSF2Event.REVERSE, this.flipIt);
                this.self.createTimer(4, 0, this.afterImage);
            };
        }

        internal function frame23():*
        {
            this.self.createTimer(1, -1, this.slowIt);
        }

        internal function frame24():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

