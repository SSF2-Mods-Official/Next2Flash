package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Jump_17 extends MovieClip {
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var xframe:*;
        public var done:*;
        public function Jump_17() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(15, frame_16);
            addFrameScript(31, frame_32);
        }
        internal function frame_1():* {
            var hand:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var xframe:*;
            var done:*;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        this.xframe = "midair";
                        this.done = false;
                        if (parent && SSF2API.isReady() && this.self && this.self.getGlobalVariable("screwAttackOn"))
                        {
                            this.self.endAttack();
                            this.self.forceAttack("item_screw");
                        };
        }
        internal function frame_16():* {
            this.self.endAttack();
        }
        internal function frame_32():* {
            this.self.endAttack();
        }
    }
}
