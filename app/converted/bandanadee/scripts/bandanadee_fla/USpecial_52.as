package bandanadee_fla
{
    import flash.display.MovieClip;
    import flash.events.Event;

    public dynamic class USpecial_52 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var sfx:*;

        public function USpecial_52()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 5, this.frame6, 6, this.frame7, 13, this.frame14, 14, this.frame15, 19, this.frame20, 20, this.frame21, 45, this.frame46, 46, this.frame47, 55, this.frame56);
        }

        public function checkDrop():void
        {
            var _local_1:* = this.self.getControls();
            if (_local_1.DOWN)
            {
                this.self.toHelpless();
            };
        }

        public function spearspin():void
        {
            SSF2API.stopSound(this.sfx);
            this.sfx = this.self.playAttackSound(1);
        }

        public function jumpToContinue(_arg_1:Event=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            this.self.destroyTimer(this.checkDrop);
            this.self.destroyTimer(this.spearspin);
            this.self.updateAttackStats({
                "air_ease":-1,
                "allowControl":false
            });
            this.self.stancePlayFrame("continue");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
        }

        internal function frame4():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame6():*
        {
            this.self.updateAttackStats({"allowControl":true});
        }

        internal function frame7():*
        {
            this.self.setYSpeed(-12.5);
        }

        internal function frame14():*
        {
            this.self.updateAttackBoxStats(1, {"damage":10});
        }

        internal function frame15():*
        {
            this.self.updateAttackStats({"air_ease":2.5});
            this.self.createTimer(1, 0, this.checkDrop);
            this.self.createTimer(8, -1, this.spearspin);
            this.sfx = this.self.playAttackSound(1);
        }

        internal function frame20():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":4,
                "power":50,
                "kbConstant":50
            });
        }

        internal function frame21():*
        {
            this.self.updateAttackStats({
                "air_ease":2,
                "refreshRate":40
            });
            if (this.self.isOnGround())
            {
                this.jumpToContinue();
            }
            else
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            };
        }

        internal function frame46():*
        {
            this.self.stancePlayFrame("freeze");
        }

        internal function frame47():*
        {
            SSF2API.stopSound(this.sfx);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bandanadee_dashstop");
            };
        }

        internal function frame56():*
        {
            this.self.endAttack();
        }


    }
}

