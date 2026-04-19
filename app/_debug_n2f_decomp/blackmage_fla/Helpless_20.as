package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Helpless_20 extends MovieClip {
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function Helpless_20() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(5, frame_6);
        }
        internal function frame_1():* {
            var hand:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }
        internal function frame_6():* {
            this.self.stancePlayFrame("redo");
        }
    }
}
