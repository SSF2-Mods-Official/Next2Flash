package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_uspec_39 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;
        public var repeat:*;
        public var effectSize:*;

        public function bomberman_uspec_39()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 11, this.frame12, 12, this.frame13, 15, this.frame16, 18, this.frame19, 21, this.frame22, 24, this.frame25, 27, this.frame28, 38, this.frame39, 39, this.frame40, 45, this.frame46);
        }

        public function flipX(_arg_1:Number):*
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function jetpackDust():void
        {
            this.self.attachEffect("dust", {
                "x":-9,
                "y":-15
            });
            this.self.attachEffect("dust", {
                "x":9,
                "y":-15
            });
        }

        public function setKB(_arg_1:*=null):*
        {
            var _local_2:* = this.self.getYSpeed();
            var _local_3:* = 90;
            if (_local_2 > 0)
            {
                _local_3 = 270;
            };
            var _local_4:* = (Math.abs(this.self.getYSpeed()) * 4);
            this.self.updateAttackBoxStats(1, {
                "direction":_local_3,
                "power":_local_4
            });
            SSF2API.print(_local_2.toString());
            SSF2API.print(((_local_3.toString() + " | ") + _local_4.toString()));
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (SSF2API.isReady() && this.self)
            {
                if (this.self.getYSpeed() > 0)
                {
                    this.self.setYSpeed(0);
                };
                this.self.attachEffect("global_sparkle", {
                    "x":this.flipX(-10),
                    "y":-15
                });
            };
        }

        internal function frame2():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame12():*
        {
            SSF2API.getCamera().shake(8);
            this.self.playAttackSound(2);
            this.self.setYSpeed(-31);
            this.self.setXSpeed(0);
            this.repeat = 1;
            this.effectSize = 1;
            this.self.attachEffect("effect_explosion", {
                "x":-9,
                "y":-28,
                "behind":true
            });
            this.self.attachEffect("effect_explosion", {
                "x":9,
                "y":-28,
                "behind":true
            });
            this.self.createTimer(3, 7, this.jetpackDust);
            this.self.updateAttackStats({
                "air_ease":-1,
                "xSpeedCap":4
            });
        }

        internal function frame13():*
        {
            this.self.updateAttackBoxStats(1, {
                "burn":false,
                "damage":1,
                "priority":2,
                "hitStun":1,
                "hitLag":-1.2,
                "selfHitStun":1,
                "effect_id":"effect_hit1",
                "direction":90,
                "kbConstant":0,
                "stackKnockback":false,
                "effectSound":"brawl_punch_s",
                "effect_id":"effect_firehit_light"
            });
            this.self.createTimer(1, -1, this.setKB);
        }

        internal function frame16():*
        {
            this.self.updateAttackStats({
                "allowControl":true,
                "air_ease":8
            });
            this.self.updateAttackBoxStats(1, {"power":120});
            this.self.refreshAttackID();
        }

        internal function frame19():*
        {
            if (this.self.isOnGround())
            {
                this.self.toHeavyLand();
            }
            else
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
                this.self.refreshAttackID();
                this.self.playAttackSound(3);
            };
        }

        internal function frame22():*
        {
            this.self.refreshAttackID();
        }

        internal function frame25():*
        {
            this.self.refreshAttackID();
        }

        internal function frame28():*
        {
            this.self.destroyTimer(this.setKB);
            this.self.updateAttackBoxStats(1, {
                "hitStun":3,
                "selfHitStun":3,
                "damage":4,
                "kbConstant":80,
                "power":80,
                "direction":80,
                "reversableAngle":true,
                "effectSound":"brawl_punch_m"
            });
            this.self.refreshAttackID();
        }

        internal function frame39():*
        {
            this.self.playAttackSound(4);
        }

        internal function frame40():*
        {
            this.self.toHelpless();
        }

        internal function frame46():*
        {
            this.self.toHelpless();
        }


    }
}

