package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class FAir_58 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var playsound:Number;
        public var audio:Number;

        public function FAir_58()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 6, this.frame7, 9, this.frame10, 10, this.frame11, 15, this.frame16, 20, this.frame21, 21, this.frame22, 28, this.frame29);
        }

        public function setAngle(_arg_1:*=null):*
        {
            var _local_2:* = this.self.getYSpeed();
            if (_local_2 > 7)
            {
                _local_2 = 7;
            };
            var _local_3:* = ((this.self.isFacingRight()) ? 10 : -10);
            var _local_4:* = (Math.atan2(_local_2, _local_3) * (-180 / Math.PI));
            var _local_5:* = (Math.sqrt(((_local_2 * _local_2) + (_local_3 * _local_3))) * 4);
            if (!this.self.isFacingRight())
            {
                _local_4 = (180 - _local_4);
            };
            if (_local_4 < 0)
            {
                _local_4 += 360;
            };
            this.self.updateAttackBoxStats(1, {
                "direction":_local_4,
                "power":_local_5
            });
            SSF2API.print(((_local_3.toString() + " | ") + _local_2.toString()));
            SSF2API.print(((_local_4.toString() + " | ") + _local_5.toString()));
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                if (this.self.getCurrentKirbyPower() != null)
                {
                    this.self.stancePlayFrame("haspower");
                };
            };
            if (this.self && SSF2API.isReady())
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame4():*
        {
            if ((this.playsound > 0.2) && (this.playsound <= 0.4) && (this.audio != 1))
            {
                this.self.playVoiceSound(1);
                this.self.setGlobalVariable("audio", 1);
            };
            if ((this.playsound > 0.4) && (this.playsound <= 0.6) && (this.audio != 2))
            {
                this.self.playVoiceSound(2);
                this.self.setGlobalVariable("audio", 2);
            };
            if ((this.playsound > 0.6) && (this.playsound <= 0.8) && (this.audio != 3))
            {
                this.self.playVoiceSound(3);
                this.self.setGlobalVariable("audio", 3);
            };
            if ((this.playsound > 0.8) && (this.playsound <= 1) && (this.audio != 4))
            {
                this.self.playVoiceSound(4);
                this.self.setGlobalVariable("audio", 4);
            };
            this.self.playAttackSound(1);
            this.self.playAttackSound(3);
            this.self.setLandingLag(true);
            this.self.createTimer(1, -1, this.setAngle);
        }

        internal function frame7():*
        {
            this.self.refreshAttackID();
        }

        internal function frame10():*
        {
            this.self.destroyTimer(this.setAngle);
            this.self.updateAttackBoxStats(1, {
                "damage":6,
                "power":30,
                "kbConstant":123,
                "hitLag":-1,
                "direction":55,
                "effectSound":"brawl_zap_m"
            });
            this.self.updateAttackBoxStats(2, {
                "damage":6,
                "power":30,
                "kbConstant":123,
                "hitLag":-1,
                "direction":55,
                "effectSound":"brawl_zap_m"
            });
            this.self.refreshAttackID();
        }

        internal function frame11():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame16():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }

        internal function frame22():*
        {
            this.self.attachEffect("effect_bdee_land", {"y":-15});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bandanadee_dashstop");
            };
        }

        internal function frame29():*
        {
            this.self.endAttack();
        }


    }
}

