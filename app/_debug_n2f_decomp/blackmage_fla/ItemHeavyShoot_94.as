package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ItemHeavyShoot_94 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function ItemHeavyShoot_94() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(3, frame_4);
            addFrameScript(25, frame_26);
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
                        this.self.attachEffect("global_dust_heavy", {
                            "x":this.self.flipX(-7),
                            "y":3,
                            "scaleX":-0.5,
                            "scaleY":-0.5
                        });
        }
        internal function frame_26():* {
            this.self.endAttack();
        }
    }
}
