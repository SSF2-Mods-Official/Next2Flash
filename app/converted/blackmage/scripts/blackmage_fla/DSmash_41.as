package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class DSmash_41 extends MovieClip
    {

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

        public function DSmash_41()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 44, this.frame45, 45, this.frame46, 46, this.frame47, 49, this.frame50, 50, this.frame51, 52, this.frame53, 56, this.frame57, 59, this.frame60, 61, this.frame62, 65, this.frame66, 72, this.frame73, 73, this.frame74, 75, this.frame76, 84, this.frame85, 85, this.frame86, 86, this.frame87, 96, this.frame97);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            this.xframe = null;
            this.blah = 0;
        }

        internal function frame4():*
        {
            this.blah = this.self.playAttackSound(1);
        }

        internal function frame5():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame45():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame46():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame47():*
        {
            this.self.addEffectToList(this.self.attachEffect("blackmage_dsmash_hands1", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame50():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame51():*
        {
            this.self.addEffectToList(this.self.attachEffect("blackmage_dsmash_ice", {
                "x":this.self.flipX(27),
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true,
                "syncHitStun":true
            }));
        }

        internal function frame53():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame57():*
        {
            SSF2API.getCamera().shake(3);
        }

        internal function frame60():*
        {
            this.self.addEffectToList(this.self.attachEffect("blackmage_dsmash_ice", {
                "x":this.self.flipX(-27),
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true,
                "syncHitStun":true
            }));
        }

        internal function frame62():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame66():*
        {
            SSF2API.getCamera().shake(3);
        }

        internal function frame73():*
        {
            this.self.endAttack();
        }

        internal function frame74():*
        {
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

        internal function frame76():*
        {
            this.self.addEffectToList(this.self.attachEffect("blackmage_dsmash_hands2", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame85():*
        {
            this.self.setGlobalVariable("destroy", "false");
        }

        internal function frame86():*
        {
            this.self.fireProjectile("dsmashfull", this.rightTrailx);
            this.rightTrail = this.self.getCurrentProjectile();
            this.self.fireProjectile("dsmashfull", this.leftTrailx);
            this.leftTrail = this.self.getCurrentProjectile();
            this.leftTrail.stancePlayFrame("left");
            this.rightTrailx += 25;
            this.leftTrailx -= 25;
            this.self.attachEffect("global_sparkle", {"y":-30});
        }

        internal function frame87():*
        {
        }

        internal function frame97():*
        {
            this.self.endAttack();
        }


    }
}

