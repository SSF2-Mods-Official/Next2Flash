package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class FAir_116 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function FAir_116()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 7, this.frame8, 8, this.frame9, 12, this.frame13, 13, this.frame14, 20, this.frame21, 26, this.frame27, 27, this.frame28, 33, this.frame34);
        }

        public function setAngle(_arg_1:*=null):*
        {
            var _local_2:* = this.self.getYSpeed();
            if (_local_2 > 0)
            {
                _local_2 = 0;
            };
            var _local_3:* = ((this.self.isFacingRight()) ? 5 : -5);
            var _local_4:* = (Math.atan2(_local_2, _local_3) * (-180 / Math.PI));
            var _local_5:* = (Math.sqrt(((_local_2 * _local_2) + (_local_3 * _local_3))) * 5);
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
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame4():*
        {
            this.self.createTimer(1, -1, this.setAngle);
        }

        internal function frame5():*
        {
            this.self.playAttackSound(1);
            this.self.setLandingLag(true);
        }

        internal function frame8():*
        {
            this.self.updateAttackBoxStats(1, {"damage":3});
            this.self.refreshAttackID();
        }

        internal function frame9():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame13():*
        {
            this.self.destroyTimer(this.setAngle);
            this.self.updateAttackBoxStats(1, {
                "damage":5,
                "power":30,
                "kbConstant":138,
                "direction":45,
                "effectSound":"brawl_kick_l"
            });
            this.self.refreshAttackID();
        }

        internal function frame14():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame21():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame27():*
        {
            this.self.endAttack();
        }

        internal function frame28():*
        {
            this.self.attachEffect("effect_kirby_land", {"y":-20});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land1");
            };
        }

        internal function frame34():*
        {
            this.self.endAttack();
        }


    }
}

