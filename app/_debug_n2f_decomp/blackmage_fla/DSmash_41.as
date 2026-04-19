package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class DSmash_41 extends MovieClip {
        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var xframe:String;
        public var blah:Number;
        public var dir:Boolean;
        public var rightTrailx:*;
        public var leftTrailx:*;
        public var rightTrail:*;
        public var leftTrail:*;
        public function DSmash_41() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(3, frame_4);
            addFrameScript(4, frame_5);
            addFrameScript(44, frame_45);
            addFrameScript(45, frame_46);
            addFrameScript(46, frame_47);
            addFrameScript(49, frame_50);
            addFrameScript(50, frame_51);
            addFrameScript(52, frame_53);
            addFrameScript(56, frame_57);
            addFrameScript(59, frame_60);
            addFrameScript(61, frame_62);
            addFrameScript(65, frame_66);
            addFrameScript(72, frame_73);
            addFrameScript(73, frame_74);
            addFrameScript(75, frame_76);
            addFrameScript(84, frame_85);
            addFrameScript(85, frame_86);
            addFrameScript(96, frame_97);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var attackBox2:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var xframe:String;
            var blah:Number;
            var dir:Boolean;
            var rightTrailx:*;
            var leftTrailx:*;
            var rightTrail:*;
            var leftTrail:*;
            if (SSF2API.isReady())
                        {
                            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        };
                        this.xframe = null;
                        this.blah = 0;
        }
        internal function frame_4():* {
            this.blah = this.self.playAttackSound(1);
        }
        internal function frame_5():* {
            this.xframe = "charging";
                        this.self.createTimer(4, -1, this.effects);
        }
        internal function frame_45():* {
            this.self.stancePlayFrame("charging");
        }
        internal function frame_46():* {
            this.xframe = "attack";
                        this.self.destroyTimer(this.effects);
        }
        internal function frame_47():* {
            this.self.addEffectToList(this.self.attachEffect("blackmage_dsmash_hands1", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
                        this.self.clearEffectsOnStateChange();
        }
        internal function frame_50():* {
            this.self.attachEffect("global_dust_swirl");
        }
        internal function frame_51():* {
            this.self.addEffectToList(this.self.attachEffect("blackmage_dsmash_ice", {
                            "x":this.self.flipX(27),
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
        }
        internal function frame_53():* {
            this.self.playAttackSound(2);
        }
        internal function frame_57():* {
            SSF2API.getCamera().shake(3);
        }
        internal function frame_60():* {
            this.self.addEffectToList(this.self.attachEffect("blackmage_dsmash_ice", {
                            "x":this.self.flipX(-27),
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
        }
        internal function frame_62():* {
            this.self.playAttackSound(2);
        }
        internal function frame_66():* {
            SSF2API.getCamera().shake(3);
        }
        internal function frame_73():* {
            this.self.endAttack();
        }
        internal function frame_74():* {
            this.xframe = "attack2";
                        this.self.destroyTimer(this.effects);
                        this.dir = this.self.isFacingRight();
                        this.self.setGlobalVariable("blackMageFacingRight", this.dir);
                        this.self.setGlobalVariable("destroy", "true");
                        this.rightTrailx = 0;
                        this.leftTrailx = 0;
                        if (this.self.isFacingRight())
                        {
                            this.rightTrailx = 25;
                            this.leftTrailx = -25;
                        }
                        else
                        {
                            this.rightTrailx = -25;
                            this.leftTrailx = 25;
                        };
                        this.rightTrail = null;
                        this.leftTrail = null;
                        this.self.playAttackSound(3);
        }
        internal function frame_76():* {
            this.self.addEffectToList(this.self.attachEffect("blackmage_dsmash_hands2", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
                        this.self.clearEffectsOnStateChange();
        }
        internal function frame_85():* {
            this.self.setGlobalVariable("destroy", "false");
        }
        internal function frame_86():* {
            this.self.fireProjectile("dsmashfull", this.rightTrailx);
                        this.rightTrail = this.self.getCurrentProjectile();
                        this.self.fireProjectile("dsmashfull", this.leftTrailx);
                        this.leftTrail = this.self.getCurrentProjectile();
                        this.leftTrail.stancePlayFrame("left");
                        this.rightTrailx += 25;
                        this.leftTrailx -= 25;
                        this.self.attachEffect("global_sparkle", {"y":-30});
        }
        internal function frame_97():* {
            this.self.endAttack();
        }
    }
}
