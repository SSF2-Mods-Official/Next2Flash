package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class FAir_71 extends MovieClip {
        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var playsound:Number;
        public function FAir_71() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(4, frame_5);
            addFrameScript(10, frame_11);
            addFrameScript(13, frame_14);
            addFrameScript(14, frame_15);
            addFrameScript(18, frame_19);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var playsound:Number;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (this.self && SSF2API.isReady())
                        {
                            this.playsound = SSF2API.random();
                            this.self.setLandingLag(false);
                        };
        }
        internal function frame_3():* {
            this.self.setLandingLag(true);
                        if ((this.self.isFacingRight() && (this.self.getXSpeed() < 8)) || (!(this.self.isFacingRight()) && (this.self.getXSpeed() > -8)))
                        {
                            this.self.setXSpeed(8, false);
                        };
                        this.self.playSound("bm_chocobocut");
                        if (this.playsound > 0.9)
                        {
                            this.self.playSound("chocobo3");
                        }
                        else if (this.playsound > 0.7)
                        {
                            this.self.playSound("chocobo2");
                        }
                        else if (this.playsound > 0.4)
                        {
                            this.self.playSound("chocobo");
                        };
        }
        internal function frame_5():* {
            this.self.attachEffect("global_dust_blast", {
                            "x":this.self.flipX(28),
                            "y":-28,
                            "parentLock":true
                        });
        }
        internal function frame_11():* {
            this.self.setLandingLag(false);
        }
        internal function frame_14():* {
            this.self.endAttack();
        }
        internal function frame_15():* {
            SSF2API.getCamera().shake(2);
                        if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_land_s");
                        }
                        else
                        {
                            this.self.playSound("blackmage_landLight");
                        };
        }
        internal function frame_19():* {
            this.self.endAttack();
        }
    }
}
