package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ItemTilt_83 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function ItemTilt_83() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(6, frame_7);
            addFrameScript(8, frame_9);
            addFrameScript(18, frame_19);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }
        internal function frame_7():* {
            this.self.getItem().activateItem();
                        this.self.attachEffect("global_dust_heavy", {
                            "x":this.self.flipX(-7),
                            "y":3,
                            "scaleX":-0.5,
                            "scaleY":-0.5
                        });
        }
        internal function frame_9():* {
            this.self.getItem().deactivateItem();
        }
        internal function frame_19():* {
            this.self.endAttack();
        }
    }
}
