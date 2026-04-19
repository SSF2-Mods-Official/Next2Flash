package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ItemHome_Run_86 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function ItemHome_Run_86() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(28, frame_29);
            addFrameScript(30, frame_31);
            addFrameScript(32, frame_33);
            addFrameScript(45, frame_46);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (this.self && SSF2API.isReady())
                        {
                            this.self.createTimer(4, -1, this.effects);
                        };
        }
        internal function frame_29():* {
            this.self.destroyTimer(this.effects);
                        this.self.updateAttackStats({"superArmor":true});
        }
        internal function frame_31():* {
            this.self.getItem().activateItem();
                        this.self.playAttackSound(1);
                        SSF2API.getCamera().shake(6);
                        this.self.attachEffect("global_dust_heavy", {
                            "x":this.self.flipX(5),
                            "y":3,
                            "scaleX":-0.75,
                            "scaleY":-0.75
                        });
        }
        internal function frame_33():* {
            this.self.getItem().deactivateItem();
                        this.self.updateAttackStats({"superArmor":false});
        }
        internal function frame_46():* {
            this.self.endAttack();
        }
    }
}
