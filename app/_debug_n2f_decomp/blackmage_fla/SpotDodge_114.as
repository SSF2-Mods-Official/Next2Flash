package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class SpotDodge_114 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function SpotDodge_114() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(1, frame_2);
            addFrameScript(10, frame_11);
            addFrameScript(13, frame_14);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            if (SSF2API.isReady())
                        {
                            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        };
        }
        internal function frame_2():* {
            this.self.attachEffect("bm_misstext", {
                            "flip":false,
                            "resize":false
                        });
                        this.self.setIntangibility(true);
                        this.self.attachEffect("global_dust_cloud", {
                            "scaleX":0.8,
                            "scaleY":0.8
                        });
        }
        internal function frame_11():* {
            this.self.setIntangibility(false);
        }
        internal function frame_14():* {
            this.self.endAttack();
        }
    }
}
