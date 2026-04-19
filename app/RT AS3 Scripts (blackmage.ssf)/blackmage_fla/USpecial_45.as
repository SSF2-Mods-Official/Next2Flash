// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.USpecial_45

package blackmage_fla
{
    import flash.display.MovieClip;
    import flash.events.Event;

    public dynamic class USpecial_45 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;
        internal var xframe:String;
        internal var projectile:*;
        internal var targetProjectile:*;

        public function USpecial_45()
        {
            addFrameScript(0, this.frame1, 1, this.frame2, 5, this.frame6, 6, this.frame7, 7, this.frame8, 22, this.frame23, 23, this.frame24, 24, this.frame25, 25, this.frame26, 33, this.frame34, 37, this.frame38);
        }

        public function removeProjectile(_arg_1:Event=null):*
        {
            if (((!(this.targetProjectile == null)) && (!(this.targetProjectile.isDisposed()))))
            {
                this.self.removeEventListener(SSF2Event.CHAR_HURT, this.removeProjectile);
                this.self.removeEventListener(SSF2Event.CHAR_KO_DEATH, this.removeProjectile);
                this.self.removeEventListener(SSF2Event.STATE_CHANGE, this.removeProjectile);
                this.targetProjectile.removeFromCamera();
                this.targetProjectile.destroy();
            };
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:BlackMageExt;
            var _local_6:String;
            var _local_7:*;
            var _local_8:*;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (((this.self) && (SSF2API.isReady())))
            {
                this.xframe = null;
                this.self.playSound("bm_Warp_part1");
                this.projectile = null;
                if (((this.self.isCPU()) && (!(this.self.isOnGround()))))
                {
                    if (this.self.inLowerLeftWarningBounds())
                    {
                        this.self.importCPUControls([6465, 56]);
                    }
                    else
                    {
                        if (this.self.inLowerRightWarningBounds())
                        {
                            this.self.importCPUControls([6721, 53]);
                        };
                    };
                };
                this.self.attachEffect("global_sparkle", {
                    "x":this.self.flipX(15),
                    "y":-20
                });
            };
        }

        internal function frame2():*
        {
            this.self.pushEffectBehind(this.self.addEffectToList(this.self.attachEffect("blackmage_uspec_start", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true
            })));
            this.self.clearEffectsOnStateChange(false);
        }

        internal function frame6():*
        {
            this.projectile = this.self.fireProjectile("warp");
            this.targetProjectile = this.projectile;
            this.projectile.addToCamera();
            this.self.addEventListener(SSF2Event.CHAR_HURT, this.removeProjectile, {"persistent":true});
            this.self.addEventListener(SSF2Event.CHAR_KO_DEATH, this.removeProjectile);
            this.self.addEventListener(SSF2Event.STATE_CHANGE, this.removeProjectile);
        }

        internal function frame7():*
        {
            this.xframe = "charging";
            if (this.self.getCurrentProjectile() != null)
            {
                this.self.getCurrentProjectile().updateProjectileStats({"controlDirection":90});
            };
        }

        internal function frame8():*
        {
            if (this.self.getCurrentProjectile() != null)
            {
                this.self.getCurrentProjectile().endControl();
            };
        }

        internal function frame23():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame24():*
        {
            this.xframe = "attack";
            this.self.playSound("bm_Warp_part2");
            this.self.removeAllEffects();
            this.self.pushEffectBehind(this.self.addEffectToList(this.self.attachEffect("blackmage_uspec_endb", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true
            })));
            this.self.addEffectToList(this.self.attachEffect("blackmage_uspec_endf", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true
            }));
            if (this.self.getCurrentProjectile() != null)
            {
                this.projectile.endControl();
            };
        }

        internal function frame25():*
        {
            if (this.self.getCurrentProjectile() != null)
            {
                this.projectile.getStanceMC().self.stancePlayFrame("continue");
            };
        }

        internal function frame26():*
        {
            this.self.updateAttackStats({"air_ease":0});
            this.self.unnattachFromGround();
            if (this.self.getCurrentProjectile() != null)
            {
                this.projectile.setXSpeed(0);
                this.projectile.setYSpeed(0);
            };
        }

        internal function frame34():*
        {
            if (this.self.getCurrentProjectile() != null)
            {
                if (((!(SSF2API.hitTestGround(this.projectile.getMC().x, (this.projectile.getMC().y - this.self.getCharacterStat("height"))))) || (!(this.projectile.isOnGround()))))
                {
                    parent.x = this.projectile.getMC().x;
                    parent.y = this.projectile.getMC().y;
                };
            };
            this.self.attachEffect("global_dust_swirl");
            this.self.removeEventListener(SSF2Event.CHAR_HURT, this.removeProjectile);
            this.self.removeEventListener(SSF2Event.CHAR_KO_DEATH, this.removeProjectile);
            this.self.removeEventListener(SSF2Event.STATE_CHANGE, this.removeProjectile);
        }

        internal function frame38():*
        {
            this.self.toHelpless();
        }


    }
}//package blackmage_fla

