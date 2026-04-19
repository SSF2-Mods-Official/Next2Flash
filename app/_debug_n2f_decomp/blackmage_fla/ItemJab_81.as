package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ItemJab_81 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function ItemJab_81() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(3, frame_4);
            addFrameScript(4, frame_5);
            addFrameScript(12, frame_13);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }
        internal function frame_4():* {
            this.self.getItem().activateItem();
                        this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
        }
        internal function frame_5():* {
            this.self.getItem().deactivateItem();
        }
        internal function frame_13():* {
            this.self.endAttack();
        }
    }
}
