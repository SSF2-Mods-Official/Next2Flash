package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Entrance_7 extends MovieClip {
        public var self:BlackMageExt;
        public function Entrance_7() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(4, frame_5);
            addFrameScript(6, frame_7);
            addFrameScript(8, frame_9);
            addFrameScript(10, frame_11);
            addFrameScript(12, frame_13);
            addFrameScript(39, frame_40);
        }
        internal function frame_1():* {
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }
        internal function frame_3():* {
            this.self.playSound("menumove");
        }
        internal function frame_5():* {
            this.self.playSound("menumove");
        }
        internal function frame_7():* {
            this.self.playSound("menumove");
        }
        internal function frame_9():* {
            this.self.playSound("menumove");
        }
        internal function frame_11():* {
            this.self.playSound("menumove");
        }
        internal function frame_13():* {
            this.self.playSound("bm_Entrance_last");
        }
        internal function frame_40():* {
            SSF2API.getCharacter(this).endAttack();
        }
    }
}
