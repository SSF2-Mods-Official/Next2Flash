package
{
    import flash.display.MovieClip;

    public dynamic class deeFinalSmashProjectile extends MovieClip
    {

        public var attackBox:MovieClip;
        public var camBox:MovieClip;
        public var self:*;
        public var owner:*;
        public var orb_sound:Number;
        public var orb_sound2:Number;
        public var PHASE_1_MAX_SPEED:Number;
        public var PHASE_1_ACCEL:Number;
        public var PHASE_1_DECEL:Number;
        public var PHASE_2_MAX_SPEED:Number;
        public var PHASE_2_ACCEL:Number;
        public var PHASE_2_DECEL:Number;
        public var currentMaxSpeed:Number;
        public var currentAccel:Number;
        public var currentDecel:Number;
        public var currentXSpeed:Number;
        public var currentYSpeed:Number;
        public var finalStart:*;
        public var firstOrbSound:*;
        public var secondOrbSound:*;
        public var scale:Number;
        public var brightness:Number;

        public function deeFinalSmashProjectile()
        {
            super();
            addFrameScript(0, this.frame1, 19, this.frame20, 35, this.frame36, 80, this.frame81, 95, this.frame96, 96, this.frame97, 114, this.frame115, 115, this.frame116);
        }

        public function trailEffectGen():void
        {
            var _local_1:MovieClip = this.self.attachEffect("dee_fs_star_trail", {
                "behind":true,
                "scaleX":3,
                "scaleY":3
            });
            var _local_2:Number = SSF2API.safeRandomInteger(0, 360);
            _local_1.x += SSF2Utils.calculateXSpeed(20, _local_2);
            _local_1.y += -(SSF2Utils.calculateYSpeed(20, _local_2));
            _local_1.rotation = _local_2;
        }

        public function orbSounds():void
        {
            this.self.stopSound(this.firstOrbSound);
            this.self.stopSound(this.secondOrbSound);
            this.self.stopSound(this.orb_sound);
            this.self.stopSound(this.orb_sound2);
            this.orb_sound = this.self.playSound("bandanadee_final_orb_00");
            this.orb_sound2 = this.self.playSound("bandanadee_final_orb_01");
        }

        public function sparkleEffectGen():void
        {
            var _local_4:Number = NaN;
            var _local_5:Number = NaN;
            var _local_1:int = 2;
            var _local_2:MovieClip;
            for (var _local_3:int = 0; _local_3 < _local_1; _local_3++)
            {
                _local_4 = SSF2API.safeRandomInteger(0, 360);
                _local_5 = SSF2API.safeRandomInteger(0, 80);
                _local_2 = this.self.attachEffect("dee_fs_sparkle", {
                    "scaleX":0.33,
                    "scaleY":0.33
                });
                _local_2.x += SSF2Utils.calculateXSpeed(_local_5, _local_4);
                _local_2.y += (-(SSF2Utils.calculateYSpeed(_local_5, _local_4)) - 50);
            };
        }

        public function controlProjectile():void
        {
            var _local_1:Object = this.owner.getControls();
            if (_local_1.LEFT && !(_local_1.RIGHT))
            {
                this.currentXSpeed -= this.currentAccel;
                if (this.currentXSpeed < -(this.currentMaxSpeed))
                {
                    this.currentXSpeed = -(this.currentMaxSpeed);
                };
            }
            else if (_local_1.RIGHT && !(_local_1.LEFT))
            {
                this.currentXSpeed += this.currentAccel;
                if (this.currentXSpeed > this.currentMaxSpeed)
                {
                    this.currentXSpeed = this.currentMaxSpeed;
                };
            }
            else if (this.currentXSpeed > 0)
            {
                this.currentXSpeed -= this.currentDecel;
                if (this.currentXSpeed < 0)
                {
                    this.currentXSpeed = 0;
                };
            }
            else if (this.currentXSpeed < 0)
            {
                this.currentXSpeed += this.currentDecel;
                if (this.currentXSpeed > 0)
                {
                    this.currentXSpeed = 0;
                };
            };
            if (_local_1.UP && !(_local_1.DOWN))
            {
                this.currentYSpeed -= this.currentAccel;
                if (this.currentYSpeed < -(this.currentMaxSpeed))
                {
                    this.currentYSpeed = -(this.currentMaxSpeed);
                };
            }
            else if (_local_1.DOWN && !(_local_1.UP))
            {
                this.currentYSpeed += this.currentAccel;
                if (this.currentYSpeed > this.currentMaxSpeed)
                {
                    this.currentYSpeed = this.currentMaxSpeed;
                };
            }
            else if (this.currentYSpeed > 0)
            {
                this.currentYSpeed -= this.currentDecel;
                if (this.currentYSpeed < 0)
                {
                    this.currentYSpeed = 0;
                };
            }
            else if (this.currentYSpeed < 0)
            {
                this.currentYSpeed += this.currentDecel;
                if (this.currentYSpeed > 0)
                {
                    this.currentYSpeed = 0;
                };
            };
            this.self.setXSpeed(this.currentXSpeed);
            this.self.setYSpeed(this.currentYSpeed);
        }

        public function expand():void
        {
            if (this.scale)
            {
                this.self.setScale(this.scale, this.scale);
                this.scale += 0.0025;
            };
        }

        public function brighten():void
        {
            SSF2Utils.setBrightness(this.self.getStanceMC(), this.brightness);
            this.brightness += 5;
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.orb_sound = 0;
            this.orb_sound2 = 1;
            this.PHASE_1_MAX_SPEED = 15;
            this.PHASE_1_ACCEL = 1;
            this.PHASE_1_DECEL = 1;
            this.PHASE_2_MAX_SPEED = 7;
            this.PHASE_2_ACCEL = 0.5;
            this.PHASE_2_DECEL = 0.5;
            this.currentMaxSpeed = 0;
            this.currentAccel = 0;
            this.currentDecel = 0;
            this.currentXSpeed = 0;
            this.currentYSpeed = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.finalStart = this.self.playSound("bandanadee_final_orb_start");
                this.self.addToCamera();
                this.owner = this.self.getOwner();
            };
        }

        internal function frame20():*
        {
            this.self.createTimer(90, -1, this.orbSounds);
        }

        internal function frame36():*
        {
            this.firstOrbSound = this.self.playSound("bandanadee_final_orb_00");
            this.secondOrbSound = this.self.playSound("bandanadee_final_orb_01");
            this.self.playSound("bandanadee_final_orb_form");
            this.self.stopSound(this.finalStart);
            SSF2API.getCamera().shake(5);
        }

        internal function frame81():*
        {
            this.scale = 1;
            this.self.createTimer(1, -1, this.expand);
            this.self.createTimer(3, -1, this.trailEffectGen);
            this.self.createTimer(3, -1, this.sparkleEffectGen);
            this.self.createTimer(1, -1, this.controlProjectile);
            this.currentMaxSpeed = this.PHASE_1_MAX_SPEED;
            this.currentAccel = this.PHASE_1_ACCEL;
            this.currentDecel = this.PHASE_1_DECEL;
            this.self.setYSpeed(8);
        }

        internal function frame96():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame97():*
        {
            this.currentMaxSpeed = this.PHASE_2_MAX_SPEED;
            this.currentAccel = this.PHASE_2_ACCEL;
            this.currentDecel = this.PHASE_2_DECEL;
            this.brightness = 0;
            this.self.destroyTimer(this.controlProjectile);
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.destroyTimer(this.trailEffectGen);
            this.self.destroyTimer(this.sparkleEffectGen);
            this.self.destroyTimer(this.expand);
            this.self.playSound("bandanadee_final_orb_end");
            this.self.stopSound(this.orb_sound);
            this.self.stopSound(this.orb_sound2);
            this.self.createTimer(1, -1, this.brighten);
            this.self.updateAttackBoxStats(1, {
                "damage":16,
                "power":90,
                "kbConstant":120
            });
            this.self.refreshAttackID();
        }

        internal function frame115():*
        {
            this.self.destroyTimer(this.brighten);
        }

        internal function frame116():*
        {
            this.self.destroy();
        }


    }
}

