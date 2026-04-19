package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ItemShoot_93 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function ItemShoot_93() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(3, frame_4);
            addFrameScript(15, frame_16);
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
        internal function frame_16():* {
            this.self.endAttack();
        }
    }
}
