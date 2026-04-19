package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Land_21 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function Land_21() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(7, frame_8);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (SSF2API.isReady() && this.self)
                        {
                            SSF2API.getCamera().shake(2);
                            if (this.self.getMetalStatus())
                            {
                                this.self.playSound("metal_land_s");
                            }
                            else
                            {
                                this.self.playSound("blackmage_landLight");
                            };
                        };
        }
        internal function frame_3():* {
            this.self.endAttack();
        }
        internal function frame_8():* {
            this.self.endAttack();
        }
    }
}
