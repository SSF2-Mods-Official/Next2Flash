package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class HeavyLand_22 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function HeavyLand_22() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(12, frame_13);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (parent && SSF2API.isReady() && this.self)
                        {
                            SSF2API.getCamera().shake(3);
                            if (this.self.getMetalStatus())
                            {
                                this.self.playSound("metal_land_m");
                            }
                            else
                            {
                                this.self.playSound("blackmage_landHeavy");
                            };
                        };
        }
        internal function frame_13():* {
            this.self.endAttack();
        }
    }
}
